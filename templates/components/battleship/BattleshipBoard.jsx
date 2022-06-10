import React, {Component} from 'react';
import PropTypes from 'prop-types';
import clsx from 'clsx';
import BattleshipSquare from './BattleshipSquare.jsx';

class BattleshipBoard extends Component {

    constructor(props) {
        super(props);
        this.isPlayerTurn = this.isPlayerTurn.bind(this);
        this.sendReset = this.sendReset.bind(this);
    }

    isPlayerTurn() {
        let turn = this.props.game.turn
        let current_user = this.props.currentUser
        let creator = this.props.game.creator
        if(turn != null) {
            return turn.id == current_user.id
        }
        else {
            // If turn is null, then it's the opponent's turn
            // basically the user that is not the creator
            return current_user.id != creator.id
        }
    }

    getOtherPlayer() {
        return this.props.game.creator.id == this.props.currentUser.id
               ? this.props.game.opponent.username
               : this.props.game.creator.username;
    }

    sendReset() {
        let message = {'action': 'reset'};
        this.props.sendSocketMessage(message);
    }

    componentDidMount() {
        this.componentDidUpdate();
    }

    componentDidUpdate() {
        // Adding some extra html to django template here
        let creator = this.props.game.creator;
        let opponent = this.props.game.opponent;
        let turn = this.props.game.turn;
        let completed = this.props.game.completed;
        let winner = this.props.game.winner;
        let current_user = this.props.currentUser;
        let html = null;
        let resultClass = null;

        html = "<div class='d-flex flex-row'>"
               +"<p class='p-0 m-0'>"+creator.username+"</p>"
               +"<p class='p-0 m-0 ms-auto'>("+this.props.game.creator_points+")</p>"
               +"</div>"
        $('#creator').html(html);

        html = "<div class='d-flex flex-row'>"
               +"<p class='p-0 m-0'>"+(opponent != null ? opponent.username : "---")+"</p>"
               +"<p class='p-0 m-0 ms-auto'>("+this.props.game.opponent_points+")</p>"
               +"</div>"
        $('#opponent').html(html);

        // Displaying result in the result-div
        if(completed) {
            // If current user is the winner
            if(current_user.id == winner.id) {
                html = "<u>Result</u>: You won";
                resultClass = 'green';
            }
            // The user participated in the game but is not the winner
            else if((current_user.id == opponent.id) || (current_user.id == creator.id)) {
                html = "<u>Result</u>: You lost"
                resultClass = 'red';
            }
            // The user did not participate in the game
            else {
                html = "<u>Result</u>: '"+winner.username+"' won";
                resultClass = 'green';
            }
            $('#result').html(html);
            $('#result-div').addClass(resultClass);

            if(winner.id == creator.id) {
                $('#creator').addClass('green');
                $('#opponent').addClass('red');
            }
            else {
                $('#opponent').addClass('green');
                $('#creator').addClass('red');
            }

            // If game has completed and the user is one of the participants,
            // enable the reset button
            if(current_user.id == creator.id || current_user.id == opponent.id) {
                $('#reset').off('click');
                $('#reset').click(() => {
                    this.sendReset();
                });
                $('#reset').prop("disabled", false);
            }
            else {
                $('#reset').prop("disabled", true);
            }
        }
        // Indicating turn in the html
        else {
            $('#reset').prop("disabled", true);
            $('#creator').removeClass('green red');
            $('#opponent').removeClass('green red');
            $('#result-div').removeClass('green red');

            if(!this.props.gameConfirmed) {
                html = "Place your ships";
            }
            else if(!this.props.game.creator_confirmed || !this.props.game.opponent_confirmed) {
                if(this.props.game.opponent == null) {
                    html = "Opponent is joining";
                }
                else {
                    let otherPlayer = this.getOtherPlayer();
                    html = "'"+otherPlayer+"' is placing ships";
                }
            }
            else {
                html = "<u>Result</u>: Ongoing";
            }

            $('#result').html(html);

            if(turn != null && turn.id == creator.id) {
                $('#creator').addClass('player-turn');
                $('#opponent').removeClass('player-turn');
            }
            else {
                $('#creator').removeClass('player-turn');
                $('#opponent').addClass('player-turn');
            }
        }
    }

    renderRow(row_index, cols) {
        let row = cols.map((square) => {
            return <BattleshipSquare key={square.id}
                               type={this.props.type}
                               squareId={square.id}
                               rowIndex={square.row}
                               colIndex={square.col}
                               attacker={square.attacker}
                               shipPiece={square.ship_piece}
                               shipDirection={square.ship_direction}
                               isBow={square.is_bow}
                               isAft={square.is_aft}
                               shipDestroyed={square.ship_destroyed}
                               gameCompleted={this.props.game.completed}
                               gameConfirmed={this.props.gameConfirmed}
                               gameStarted={this.props.gameStarted}
                               isPlayerTurn={this.isPlayerTurn}
                               sendSocketMessage={this.props.sendSocketMessage}
                               />;
        });

        return (
            <tr key={row_index} className="d-flex w-100 justify-content-center">
            <td className="m-0 p-0"><p className="table-first-col">{row_index + 1}</p></td>
            {row}
            </tr>
        );
    }

    renderBoard() {
        let board = [];
        let current_row = -1;
        if(this.props.game != null && this.props.squares != null) {

            if(!this.props.gameConfirmed) {
                $('#reset').html('Confirm');
                $('#reset').prop('disabled', false);
            }

            board = this.props.squares.map((square) => {
                if(square.row != current_row) {
                    // New row
                    current_row = square.row;
                    let row_cols = this.props.squares.filter((c) => {
                        if(c.row === current_row) {
                            return c;
                        }
                    })
                    return this.renderRow(current_row, row_cols);
                }
            }, this);
        }
        else {
            board = <tr><td>LOADING</td></tr>;
        }
        return board;
    }

    render() {
        let className = clsx(
            'default-cell',
            'table-header',
            'p-0',
            'm-0'
        );
        return (
            <table className="w-100">

            <thead>
                <tr className="d-flex w-100 justify-content-center">
                    <td className="m-0 p-0"><p className="table-first-col table-hash">#</p></td>
                    <td className={className}>A</td>
                    <td className={className}>B</td>
                    <td className={className}>C</td>
                    <td className={className}>D</td>
                    <td className={className}>E</td>
                    <td className={className}>F</td>
                    <td className={className}>G</td>
                    <td className={className}>H</td>
                    <td className={className}>I</td>
                    <td className={className}>J</td>
                </tr>
            </thead>

            <tbody>
            {this.renderBoard()}
            </tbody>

            </table>
        );
    }
}

BattleshipBoard.propTypes = {
    currentUser: PropTypes.object,
    type: PropTypes.string,
    game: PropTypes.object,
    gameConfirmed: PropTypes.bool,
    gameStarted: PropTypes.bool,
    squares: PropTypes.array,
    sendSocketMessage: PropTypes.func
};


export default BattleshipBoard;
