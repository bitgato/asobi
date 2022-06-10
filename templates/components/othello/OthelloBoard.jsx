import React, {Component} from 'react';
import PropTypes from 'prop-types';
import ClaimingGameBoard from '../ClaimingGameBoard.jsx';
import OthelloSquare from './OthelloSquare.jsx';

class OthelloBoard extends ClaimingGameBoard {

	componentDidMount() {
		const gameUrl = location.protocol+'//'+location.host+'/othello-from-code/'+this.props.gc;
		super.componentDidMount(gameUrl);
	}

	setSymbols() {
		let creator = this.state.game.creator;
		let opponent = this.state.game.opponent;
		let html;
		html = "<div class='d-flex flex-row align-items-center'>"
			+"<div class='p-0 mb-1 me-2'>("+this.state.game.creator_pts+")</div>"
			+"<div class='p-0 mb-1'>"+creator.username+"</div>"
			+"<div class='p-0 m-0 rounded-circle player-color black ms-auto'></div>"
			+"</div>"
		$('#creator').html(html);

		html = "<div class='d-flex flex-row align-items-center'>"
			+"<div class='p-0 mb-1 me-2'>("+this.state.game.opponent_pts+")</div>"
			+"<div class='p-0 mb-1'>"+(opponent != null ? opponent.username : "---")+"</div>"
			+"<div class='p-0 m-0 rounded-circle player-color white ms-auto'></div>"
			+"</div>"
		$('#opponent').html(html);
	}

	renderRow(rowIndex, cols) {
		let row = cols.map((square) => {
			let playerWon = false;
			let playerLost = false;
			let tie = false;
			if(this.state.game.completed) {
				let currentUser = this.props.currentUser;
				let winner = this.state.game.winner;
				let creator = this.state.game.creator;
				let opponent = this.state.game.opponent;

				if(winner == null) {
					tie = true;
				}
				else {
					if(square.winning_square) {
						if(winner.id == currentUser.id) {
							playerWon = true;
						}
						else {
							playerLost = true;
						}
					}
					// If the user didn't participate in the match then show green squares
					if(currentUser.id != creator.id && currentUser.id != opponent.id) {
						playerWon = true;
						playerLost = false;
					}
				}
			}
			return <OthelloSquare key={square.id}
							   gameCreator={this.state.game.creator.id}
			                   owner={square.owner}
			                   lastMove={this.state.game.last_move}
			                   squareId={square.id}
			                   movable={square.movable}
			                   playerWon={playerWon}
			                   playerLost={playerLost}
			                   tie={tie}
			                   gameCompleted={this.state.game.completed}
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

OthelloBoard.propTypes = {
	gc: PropTypes.string,
	socket: PropTypes.string,
	currentUser: PropTypes.object
};


export default OthelloBoard;
