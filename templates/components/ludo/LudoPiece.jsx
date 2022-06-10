import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {createRoot} from 'react-dom/client';
import clsx from 'clsx';
import WebSocket from 'react-websocket';
import ReactDOM from 'react-dom';

class LudoPiece extends Component {

    constructor(props) {
        super(props);
        this.state = {
            position: null
        }
        this.pieceClicked = this.pieceClicked.bind(this);
        this.renderPiece = this.renderPiece.bind(this);
    }

    movePiece() {
        let message = {
            'action': 'move',
            'id': this.props.pieceId
        };
        this.props.sendSocketMessage(message);
    }

    renderPiece() {
        let className = clsx(
            'ludo-piece',
            this.canMove() && 'can-move',
            this.props.getColor(this.props.player.player_number)
        );
        let pieceId = "piece-"+this.props.pieceId;
        let html = "<button id='"+pieceId+"' class='"+className+"'></button>";
        pieceId = '#'+pieceId;
        if(this.props.player.player_number == this.props.currentPlayerNumber
            && this.props.finished) {
            let trayId = 'finished-piece-'+this.props.pieceNumber;
            $('#'+trayId).html(html);
            $(pieceId).prop("disabled", true);
            return;
        }
        $('#'+this.getCellID()).append(html);
        $(pieceId).click(() => {
            this.movePiece();
        })
        if(this.props.player.user.id == this.props.currentUserId) {
            $(pieceId).css("zIndex", 1);
        }
        else {
            $(pieceId).css("zIndex", 0);
        }
        if(this.canMove()) {
            $(pieceId).prop("disabled", false);
        }
        else {
            $(pieceId).prop("disabled", true);
        }
    }

    clearPiece(prevProps) {
        let pieceId = "piece-"+prevProps.pieceId;
        $('#'+pieceId).remove();
    }

    componentDidMount() {
        this.setState({
            position: this.props.position
        })
        this.renderPiece();
    }

    componentDidUpdate(prevProps) {
        if(prevProps.position != this.props.position) {
            this.setState({
                position: this.props.position
            })
        }
        this.clearPiece(prevProps);
        this.renderPiece();
    }

    getCellID(prevProps=null) {
        let props = prevProps || this.props;
        if(props.position == 0) {
            switch(props.player.player_number) {
                case 0: return "RH-" + props.pieceNumber;
                case 1: return "GH-" + props.pieceNumber;
                case 2: return "YH-" + props.pieceNumber;
                case 3: return "BH-" + props.pieceNumber;
            }
        }
        return "cell-" + props.position;
    }

    canMove() {
        return (
            (!this.props.gameCompleted) &&
            (this.props.player.status == 'Selecting') &&
            (this.props.player.player_number == this.props.currentPlayerNumber) &&
            this.props.canMove
        );
    }

    pieceClicked(piece) {
        if(this.canMove()) {
            this.movePiece();
        }
    }

    render() {
        return null;
    }

}

LudoPiece.propTypes = {
    pieceId: PropTypes.number,
    position: PropTypes.number,
    pieceNumber: PropTypes.number,
    player: PropTypes.object,
    currentUserId: PropTypes.number,
    currentPlayerNumber: PropTypes.number,
    canMove: PropTypes.bool,
    finished: PropTypes.bool,
    gameCompleted: PropTypes.bool,
    sendSocketMessage: PropTypes.func,
    getColor: PropTypes.func
};

export default LudoPiece;
