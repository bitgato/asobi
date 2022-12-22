import React, {Component} from 'react';
import PropTypes from 'prop-types';
import clsx from 'clsx';
import ClaimingGameSquare from '../ClaimingGameSquare.jsx';

class OthelloSquare extends ClaimingGameSquare {

    constructor(props) {
        super(props)
        this.state = {...this.state}
        this.squareClicked = this.squareClicked.bind(this)
    }

    getDisc() {
        let dot = "";
        let lastMove = this.props.lastMove;
        if(lastMove != null && lastMove.id == this.props.squareId) {
             dot = <div className="othello-red-dot"></div>;
        }
        if(this.props.owner == 'Black') {
            return <div className="othello-disc black">{dot}</div>;
        }
        else if(this.props.owner == 'White') {
            return <div className="othello-disc white">{dot}</div>;
        }
        else if(this.props.isPlayerTurn() && this.props.movable) {
            return <div className="othello-disc movable">{dot}</div>;
        }
        else {
            return null;
        }
    }

    isAvailable() {
        if(this.props.movable && this.props.isPlayerTurn()) {
            return (!this.props.gameCompleted) && (this.props.owner == 'None');
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
            'dark-green',
            playerLost && 'red',
            playerWon && 'green',
            tie && 'yellow'
        );
        return (
            <button onClick={this.squareClicked}
                    disabled={this.state.disabled || !this.isAvailable()}
                    className={className}>
                {this.getDisc()}
            </button>
        );
    }
}

OthelloSquare.propTypes = {
    squareId: PropTypes.number,
    owner: PropTypes.string,
    lastMove: PropTypes.object,
    gameCreator: PropTypes.number,
    playerWon: PropTypes.bool,
    playerLost: PropTypes.bool,
    tie: PropTypes.bool,
    gameCompleted: PropTypes.bool,
    sendSocketMessage: PropTypes.func,
    isPlayerTurn: PropTypes.func
};

export default OthelloSquare;
