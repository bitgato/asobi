import React, {Component} from 'react';
import PropTypes from 'prop-types';
import ClaimingGameBoard from '../ClaimingGameBoard.jsx';
import ObstructionSquare from './ObstructionSquare.jsx';

class ObstructionBoard extends ClaimingGameBoard {

	componentDidMount() {
		const gameUrl = location.protocol+'//'+location.host+'/obstruction-from-code/'+this.props.gc;
		super.componentDidMount(gameUrl);
	}

	setSymbols() {
		let creator = this.state.game.creator;
		let opponent = this.state.game.opponent;
		let html;
		html = "<div class='d-flex flex-row'>"
			+"<p class='p-0 m-0'>"+creator.username+"</p>"
			+"<p class='p-0 m-0 ms-auto'>X</p>"
			+"</div>"
		$('#creator').html(html);

		html = "<div class='d-flex flex-row'>"
			+"<p class='p-0 m-0'>"+(opponent != null ? opponent.username : "---")+"</p>"
			+"<p class='p-0 m-0 ms-auto'>O</p>"
			+"</div>"
		$('#opponent').html(html);
	}

	renderRow(rowIndex, cols) {
		let row = cols.map((square) => {
			return <ObstructionSquare key={square.id}
							   gameCreator={this.state.game.creator.id}
			                   owner={square.owner}
			                   squareId={square.id}
			                   status={square.status}
			                   game_completed={this.state.game.completed}
			                   sendSocketMessage={this.sendSocketMessage}
			                   isPlayerTurn={this.isPlayerTurn}
			                   />;
		})

		return (
			<div key={rowIndex} className="d-flex w-100 justify-content-center">
			{row}
			</div>
		);
	}
}

ObstructionBoard.propTypes = {
	gc: PropTypes.string,
	socket: PropTypes.string,
	currentUser: PropTypes.object
};


export default ObstructionBoard;
