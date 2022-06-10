import React, {Component} from 'react';
import PropTypes from 'prop-types';
import WebSocket from 'react-websocket';
import $ from 'jquery';
import BattleshipBoard from './BattleshipBoard.jsx';
import BattleshipPort from './BattleshipPort.jsx';

class BattleshipWrapper extends Component {

    constructor(props) {
        super(props);
        this.state = {
            game: null,
            mySquares: null,
            oppSquares: null
        }
        this.sendSocketMessage = this.sendSocketMessage.bind(this);
        this.sendConfirm = this.sendConfirm.bind(this);
        this.handleData = this.handleData.bind(this);
        this.gameConfirmed = this.gameConfirmed.bind(this);
    }

    // Set mySquares and oppSquares depending on whether the user
    // is the creator or the oppoent in the game
    setSquares(result) {
        if(this.props.currentUser.id == result.game.creator.id) {
            this.setState({
                game: result.game,
                mySquares: result.creator_squares,
                oppSquares: result.opponent_squares
            });
        }
        else {
            this.setState({
                game: result.game,
                mySquares: result.opponent_squares,
                oppSquares: result.creator_squares
            });
        }
    }

    componentDidMount() {
        let gc = this.props.gc;
        let user_id = this.props.currentUser.id;
        const game_url = location.protocol+'//'+location.host+'/battleship-from-code/'+gc;
        this.serverRequest = $.get(game_url, (result) => {
            this.setSquares(result);
        })
        $('#reset').click(() => {
            this.sendConfirm();
        })
    }

    componentDidUpdate(prevProps) {
        if(this.gameConfirmed()) {
            $('div[id^=div-]').attr('draggable', false);
        }
    }

    componentWillUnmount() {
        this.serverRequest.abort()
    }

    gameConfirmed() {
        return this.props.currentUser.id == this.state.game.creator.id
               ? this.state.game.creator_confirmed
               : this.state.game.opponent_confirmed;
    }

    gameStarted() {
        return this.state.game.creator_confirmed
               && this.state.game.opponent_confirmed;
    }

    sendConfirm() {
        var shipDirections = [];
        var shipSquares = [[], [], [], [], [], [], []];
        for(let i=0; i<7; i++) {
            $('div[data-shipnum='+(i + 1)+']').each(function(index) {
                shipSquares[i].push($(this).attr('data-squareid'));
            });
            shipDirections.push($('.first div[data-shipnum='+(i + 1)+']').attr('data-direction'));
        }
        let message = {
            'action': 'confirm',
            'Carrier': {
                'direction': shipDirections[0],
                'squares': shipSquares[0],
            },
            'Battleship': {
                'direction': shipDirections[1],
                'squares': shipSquares[1],
            },
            'Cruiser': {
                'direction': shipDirections[2],
                'squares': shipSquares[2],
            },
            'Submarine1': {
                'direction': shipDirections[3],
                'squares': shipSquares[3],
            },
            'Submarine2': {
                'direction': shipDirections[4],
                'squares': shipSquares[4],
            },
            'Destroyer1': {
                'direction': shipDirections[5],
                'squares': shipSquares[5],
            },
            'Destroyer2': {
                'direction': shipDirections[6],
                'squares': shipSquares[6],
            }
        };
        this.sendSocketMessage(message);
        $('#reset').html('Reset');
    }

    handleData(data) {
        let result = JSON.parse(data);
        this.setSquares(result);
    }

    sendSocketMessage(message) {
        let socket = this.refs.socket;
        socket.state.ws.send(JSON.stringify(message));
    }

    render() {
        if(this.state.game != null) {
            let gameConfirmed = this.gameConfirmed();
            let gameStarted = this.gameStarted();
            return (
                <>
                <div className="col d-flex flex-column mx-0 px-0 align-items-center">
                    <div id="attacks">
                        <BattleshipBoard currentUser={this.props.currentUser}
                                         type='attack'
                                         game={this.state.game}
                                         gameConfirmed={gameConfirmed}
                                         gameStarted={gameStarted}
                                         squares={this.state.oppSquares}
                                         sendSocketMessage={this.sendSocketMessage}/>
                    </div>
                    <BattleshipPort gameConfirmed={gameConfirmed}/>
                </div>
                <div id="ship-placement" className="col-8 ms-2 px-0">
                    <BattleshipBoard currentUser={this.props.currentUser}
                                     type='placement'
                                     game={this.state.game}
                                     gameConfirmed={gameConfirmed}
                                     gameStarted={gameStarted}
                                     squares={this.state.mySquares}
                                     sendSocketMessage={this.sendSocketMessage}/>
                </div>
                <WebSocket ref="socket"
                           url={this.props.socketUrl}
                           onMessage={this.handleData}
                           reconnect={true}/>
                </>
            );
        }
    }
}

BattleshipWrapper.propTypes = {
    currentUser: PropTypes.object,
    socketUrl: PropTypes.string,
    gc: PropTypes.string
}

export default BattleshipWrapper;
