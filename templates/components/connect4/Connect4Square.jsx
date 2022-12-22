import React, {Component} from 'react';
import PropTypes from 'prop-types';
import ReactDOM from 'react-dom';
import clsx from 'clsx';
import ClaimingGameSquare from '../ClaimingGameSquare.jsx';

class Connect4Square extends ClaimingGameSquare {

    constructor(props) {
        super(props)
        this.state = {...this.state}
        this.squareClicked = this.squareClicked.bind(this)
        this.drop = this.drop.bind(this)
    }

    resize() {
        var $this = $(ReactDOM.findDOMNode(this));
        let width = $this.width();
        // First row has buttons for dropping
        if(this.props.row == 0) {
            // 4px less to account for the borders
            $this.find('.default-cell').height(width - 4);
        }
        else {
            $this.height(width);
        }
    }

    isAvailable() {
        if(this.props.isPlayerTurn()) {
            return (!this.props.gameCompleted) && (this.props.owner == null);
        }
        else {
            return false;
        }
    }

    drop() {
        let message = {
            'action': 'drop',
            'col': this.props.col
        }
        this.props.sendSocketMessage(message)
    }

    canDrop() {
        return !this.props.gameCompleted
               && this.props.isPlayerTurn()
               && this.props.owner == null;
    }

    ownedByCreator() {
        return this.props.owner != null
               && this.props.owner == this.props.gameCreator;
    }

    ownedByOpponent() {
        return this.props.owner != null
               && this.props.owner != this.props.gameCreator;
    }

    render() {
        let playerWon = this.props.playerWon;
        let playerLost = this.props.playerLost;
        let tie = this.props.tie;
        let row0ClassName = clsx(
            'd-flex',
            'flex-column',
            'justify-content-center',
            'align-items-center',
            'w-100'
        );
        let containerClassName = clsx(
            'default-cell',
            'connect4-board'
        );
        let circleClassName = clsx(
            'connect4-circle',
            this.ownedByCreator() && 'red',
            this.ownedByOpponent() && 'yellow',
            this.props.winningSquare && 'rotating-circle',
        );
        if(this.props.row == 0) {
            return (
                <div className={row0ClassName}>
                    <button className="drop-button mb-2 p-0"
                            data-col={this.props.col}
                            disabled={this.state.disabled || !this.canDrop()}
                            onClick={this.drop}>Drop</button>
                    <div className={containerClassName}>
                        <div className="connect4-slot">
                            <div className={circleClassName}></div>
                        </div>
                    </div>
                </div>
            )
        }
        else {
            return (
                <div className={containerClassName}>
                    <div className="connect4-slot">
                        <div className={circleClassName}></div>
                    </div>
                </div>
            );
        }
    }
}

Connect4Square.propTypes = {
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

export default Connect4Square;
