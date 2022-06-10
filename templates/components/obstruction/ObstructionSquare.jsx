import React, {Component} from 'react';
import PropTypes from 'prop-types';
import clsx from 'clsx';
import ClaimingGameSquare from '../ClaimingGameSquare.jsx';

class ObstructionSquare extends ClaimingGameSquare {

    getSymbol() {
        let symbol = "";
        if(this.props.owner != null && this.props.status != 'Surrounding') {
            symbol = (this.props.owner == this.props.gameCreator) ? "X" : "O";
        }
        return <p>{symbol}</p>;
    }

    isAvailable() {
        if(this.props.isPlayerTurn()) {
            return (!this.props.gameCompleted) && (this.props.status == 'Free');
        }
        else {
            return false;
        }
    }

    render() {
        let creatorSq = false;
        let opponentSq = false;
        let creatorSurrSq = false;
        let opponentSurrSq = false;
        if(this.props.status == 'Selected') {
            creatorSq = this.props.owner == this.props.gameCreator
            opponentSq = !creatorSq
        }
        if(this.props.status == 'Surrounding') {
            creatorSurrSq = this.props.owner == this.props.gameCreator
            opponentSurrSq = !creatorSurrSq
        }
        let className = clsx(
            'default-cell',
            creatorSq && 'dark-blue',
            creatorSurrSq && 'blue',
            opponentSq && 'dark-red',
            opponentSurrSq && 'red',
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

ObstructionSquare.propTypes = {
    squareId: PropTypes.number,
    owner: PropTypes.number,
    gameCreator: PropTypes.number,
    gameCompleted: PropTypes.bool,
    sendSocketMessage: PropTypes.func,
    isPlayerTurn: PropTypes.func
};

export default ObstructionSquare;
