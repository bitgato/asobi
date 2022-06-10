import React, {Component} from 'react';
import PropTypes from 'prop-types';
import ClaimingGameBoard from '../ClaimingGameBoard.jsx';
import TicTacToeSquare from './TicTacToeSquare.jsx';

class TicTacToeBoard extends ClaimingGameBoard {

	componentDidMount() {
		const gameUrl = location.protocol+'//'+location.host+'/tictactoe-from-code/'+this.props.gc;
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
			return <TicTacToeSquare key={square.id}
							   gameCreator={this.state.game.creator.id}
			                   owner={square.owner}
			                   squareId={square.id}
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

TicTacToeBoard.propTypes = {
	gc: PropTypes.string,
	socket: PropTypes.string,
	currentUser: PropTypes.object
};


export default TicTacToeBoard;
