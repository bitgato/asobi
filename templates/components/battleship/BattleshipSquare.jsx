import React, {Component} from 'react';
import PropTypes from 'prop-types';
import clsx from 'clsx';
import ReactDOM from 'react-dom';

class BattleshipSquare extends Component {

    constructor(props) {
        super(props);
        this.onDrop = this.onDrop.bind(this);
        this.allowDrop = this.allowDrop.bind(this);
        if(this.props.type == 'placement') {
            this.onDrag = this.onDrag.bind(this);
            this.rotate = this.rotate.bind(this);
        }
        this.canFit = this.canFit.bind(this);
        this.resize = this.resize.bind(this);
        if(this.props.type == 'attack') {
            this.attackSquare = this.attackSquare.bind(this);
            this.isAttackable = this.isAttackable.bind(this);
        }
    }

    resize() {
        var $this = $(ReactDOM.findDOMNode(this))
        let width = $this.width()
        $this.height(width)
    }

    componentDidMount() {
        window.addEventListener('resize', this.resize)
        this.resize()
    }

    getDivId(colIndex=this.props.colIndex) {
        return 'div-'+this.props.rowIndex+'-'+colIndex;
    }

    getSquareId(colIndex=this.props.colIndex) {
        return 'square-'+this.props.rowIndex+'-'+colIndex;
    }

    getSize(type) {
        switch(type) {
            case "carrier": return 5;
            case "battleship": return 4;
            case "cruiser": return 3;
            case "submarine": return 2;
            case "destroyer": return 1;
        }
    }

    canFit(direction, size) {
        return (direction == 'row' && (10 - this.props.colIndex) >= size) ||
               (direction == 'column' && (10 - this.props.rowIndex) >= size);
    }

    canMove(type, direction, shipNum) {
        let size = this.getSize(type);
        for(let i=0; i<size; i++) {
            let id;
            if(direction == 'row') {
                id = '#'+this.getSquareId(this.props.colIndex + i);
            }
            else {
                id = '#square-'+(this.props.rowIndex + i)+'-'+this.props.colIndex;
            }
            let cls = 'has-ship';
            let otherShipNum = $(id).children().attr('data-shipnum');
            if((otherShipNum != shipNum) && $(id).hasClass(cls)) {
                return false;
            }
        }
        return true;
    }

    removeHighlight(type, row, col, direction) {
        let size = this.getSize(type);
        if(!this.canFit(direction, size)) {return false;}
        row = parseInt(row);
        col = parseInt(col);
        for(let i=0; i<size; i++) {
            let id;
            if(direction == 'row') {
                id = '#square-'+row+'-'+(col+i);
            }
            else {
                id = '#square-'+(row+i)+'-'+col;
            }
            $(id).removeClass('has-ship first last horizontal vertical');
            $(id).children().removeAttr('data-shipnum');
            $(id).children().removeAttr('data-ship');
        }
        return true;
    }

    highlight(type, direction, shipNum) {
        let size = this.getSize(type);
        if(!this.canFit(direction, size)) {return;}
        for(let i=0; i<size; i++) {
            let id;
            if(direction == 'row') {
                id = '#'+this.getSquareId(this.props.colIndex + i);
            }
            else {
                id = '#square-'+(this.props.rowIndex + i)+'-'+(this.props.colIndex);
            }
            let cls = clsx(
                'has-ship',
                (direction == 'row') && 'horizontal',
                (direction == 'column') && 'vertical',
                (i == 0) && 'first',
                i == (size - 1) && 'last',
            )
            $(id).addClass(cls);
            $(id).children().attr('data-shipnum', shipNum);
            if(i == 0){
                $(id).children().attr('data-ship', type);
                $(id).children().attr('data-direction', direction);
            }
        }
    }

    highlightDiv(divId) {
        let id = '#'+divId;
        let row = $(id).attr('data-row');
        let col = $(id).attr('data-col');
        let type = $(id).attr('data-ship');
        let shipNum = $(id).attr('data-shipnum');
        let direction = $(id).attr('data-direction');
        if(!$(id).parent().hasClass('first')) {
            return;
        }
        if(!this.canMove(type, direction, shipNum)) {
            return;
        }
        this.removeHighlight(type, row, col, direction);
        this.highlight(type, direction, shipNum);
    }

    allowDrop(ev) {
        ev.preventDefault();
    }

    onDrop(ev) {
        ev.preventDefault();
        let id = ev.dataTransfer.getData('text');
        let size = this.getSize(id);
        if(id.startsWith('div-')) {
            this.highlightDiv(id);
        }
        else {
            let direction = 'row';
            let shipNum = $('#'+id).attr('data-shipnum');
            let shipsLeft = $('#'+id).attr('data-shipsleft');
            let divId = this.getDivId();
            if($('#'+divId).attr('data-shipnum')) {
                return;
            }
            if(!this.canFit(direction, size)
                || !this.canMove(id, direction, shipNum)) {
                return;
            }
            if(shipsLeft == 1) {
                // Remove parent to remove the tooltip as well
                $('#'+id).parent().remove();
                // If all ships have been placed on the board
                if(!$.trim($('#ship-port').html()).length) {
                    $('#ship-port').html('Empty');
                    $('#reset').prop('disabled', false);
                }
            }
            else {
                shipNum = parseInt(shipNum);
                $('#'+id).attr('data-shipnum', (shipNum + 1));
                $('#'+id).attr('data-shipsleft', (shipsLeft - 1));
            }
            this.highlight(id, direction, shipNum);
        }
    }

    onDrag(ev) {
        ev.dataTransfer.setData('text', ev.target.id);
    }

    rotate() {
        let id = '#'+this.getDivId();
        let row = $(id).attr('data-row');
        let col = $(id).attr('data-col');
        let direction = $(id).attr('data-direction');
        let type = $(id).attr('data-ship');
        let shipNum = $(id).attr('data-shipnum');
        let size = this.getSize(type);
        let newDirection;
        if(direction == 'row') {newDirection = 'column';}
        else {newDirection = 'row';}
        if(!this.canFit(newDirection, size)) {return;}
        if(!this.canMove(type, newDirection, shipNum)) {
            return;
        }
        this.removeHighlight(type, row, col, direction);
        this.highlight(type, newDirection, shipNum);
    }

    attackSquare() {
        let message = {
            'action': 'attack',
            'square_id': this.props.squareId,
        }
        this.props.sendSocketMessage(message);
    }

    isAttackable() {
        return this.props.gameStarted
               && !this.props.gameCompleted
               && (this.props.attacker == null);
    }

    attackHit() {
        return this.props.attacker != null && this.props.shipPiece != 'Blank';
    }

    render() {
        let playerWon = this.props.playerWon;
        let playerLost = this.props.playerLost;
        let tie = this.props.tie;
        let confirmed = this.props.gameConfirmed;
        let isPlayerTurn = this.props.isPlayerTurn();
        let isAttackable = this.isAttackable();
        let placementClasses = clsx(
            'default-cell',
            'battleship-square',
            'm-0',
            'p-0',
            confirmed && this.props.shipPiece != 'Blank' && 'has-ship',
            confirmed && this.props.shipDirection == 'Row' && 'horizontal',
            confirmed && this.props.shipDirection == 'Column' && 'vertical',
            confirmed && this.props.isBow && 'first',
            confirmed && this.props.isAft && 'last',
            confirmed && this.props.gameConfirmed && 'confirmed',
            this.props.attacker != null && 'attacked',
            this.attackHit() && 'hit',
        );
        let attackClasses = clsx(
            'default-cell',
            'battleship-square',
            'm-0',
            'p-0',
            this.props.attacker != null && 'attacked',
            this.attackHit() && 'hit',
        );
        let squareId = this.getSquareId();
        let divId = this.getDivId();
        if(this.props.type == 'attack') {
            squareId = 'attack-'+squareId;
            divId = 'attack-'+divId;
            return (
                <td id={squareId}
                    className={this.props.shipDestroyed
                               ? placementClasses
                               : attackClasses}>
                    <button id={divId}
                         disabled={!isPlayerTurn || !isAttackable}
                         className="default-cell w-100 h-100"
                         onDragStart={this.onDrag}
                         data-row={this.props.rowIndex}
                         data-col={this.props.colIndex}
                         data-squareid={this.props.squareId}
                         onClick={this.attackSquare}>
                         {this.props.attacker != null && <p>X</p>}
                         </button>
                    <span className="explosion explosion1"></span>
                    <span className="explosion explosion2"></span>
                    <span className="explosion explosion3"></span>
                    <span className="explosion explosion4"></span>
                </td>
            );
        }
        else {
            return (
                <td id={squareId}
                    className={placementClasses}
                    onDrop={this.onDrop}
                    onDragOver={this.allowDrop}>
                    <div id={divId}
                         className="w-100 h-100"
                         draggable="true"
                         onDragStart={this.onDrag}
                         data-direction="row"
                         data-row={this.props.rowIndex}
                         data-col={this.props.colIndex}
                         data-squareid={this.props.squareId}>
                         {this.props.attacker != null && <p>X</p>}
                         <span className="rotate"
                               onClick={this.rotate}>&#10227;</span>
                         </div>
                </td>
            );
        }
    }
}

BattleshipSquare.propTypes = {
    type: PropTypes.string,
    squareId: PropTypes.number,
    rowIndex: PropTypes.number,
    colIndex: PropTypes.number,
    attacker: PropTypes.number,
    shipPiece: PropTypes.string,
    shipDirection: PropTypes.string,
    isBow: PropTypes.bool,
    isAft: PropTypes.bool,
    shipDestroyed: PropTypes.bool,
    gameCompleted: PropTypes.bool,
    gameConfirmed: PropTypes.bool,
    gameStarted: PropTypes.bool,
    isPlayerTurn: PropTypes.func,
    sendSocketMessage: PropTypes.func
};

export default BattleshipSquare;
