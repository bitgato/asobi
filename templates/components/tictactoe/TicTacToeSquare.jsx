import React, {Component} from 'react';
import PropTypes from 'prop-types';
import clsx from 'clsx';
import ClaimingGameSquare from '../ClaimingGameSquare.jsx';

class TicTacToeSquare extends ClaimingGameSquare {

    constructor(props) {
        super(props)
        this.squareClicked = this.squareClicked.bind(this)
    }

    getSymbol() {
        let symbol = "";
        if(this.props.owner != null) {
            symbol = (this.props.owner == this.props.gameCreator) ? "X" : "O";
        }
        return <p>{symbol}</p>;
    }

    isAvailable() {
        if(this.props.isPlayerTurn()) {
            return (!this.props.gameCompleted) && (this.props.owner == null);
        }
        else {
            return false;
        }
    }

    render() {
        let playerWon = this.props.playerWon;
        let playerLost = this.props.playerLost;
        let tie = this.props.tie;
        let className = clsx(
            'default-cell',
            playerLost && 'red',
            playerWon && 'green',
            tie && 'yellow'
        );
        return (
            <button onClick={this.squareClicked}
                    disabled={!this.isAvailable()}
                    className={className}>
                {this.getSymbol()}
            </button>
        );
    }
}

TicTacToeSquare.propTypes = {
    squareId: PropTypes.number,
    owner: PropTypes.number,
    gameCreator: PropTypes.number,
    playerWon: PropTypes.bool,
    playerLost: PropTypes.bool,
    tie: PropTypes.bool,
    gameCompleted: PropTypes.bool,
    sendSocketMessage: PropTypes.func,
    isPlayerTurn: PropTypes.func
};

export default TicTacToeSquare;
