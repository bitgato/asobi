import React, {Component} from 'react';
import $ from 'jquery';
import WebSocket from 'react-websocket'

class ClaimingGameBoard extends Component {

	constructor(props) {
		super(props)
		this.state = {
			game: null,
			squares: null,
		}
		this.sendSocketMessage = this.sendSocketMessage.bind(this)
		this.isPlayerTurn = this.isPlayerTurn.bind(this)
	}

	componentDidMount(gameUrl) {
		this.serverRequest = $.get(gameUrl, (result) => {
			this.setState({
				game: result.game,
				squares: result.squares
			})
		})

		$('#reset').click(() => {
			let message = {'action': 'reset'};
			this.sendSocketMessage(message);
		});
	}

	componentWillUnmount() {
		this.serverRequest.abort()
	}

	sendSocketMessage(message) {
		const socket = this.refs.socket
		socket.state.ws.send(JSON.stringify(message))
	}

	displayResult() {
		let winner = this.state.game.winner;
		let creator = this.state.game.creator;
		let opponent = this.state.game.opponent;
		let currentUser = this.props.currentUser;

		let resultClass, html;

		// If no winner
		if(winner == null) {
			html = "<u>Result</u>: It's a tie";
			resultClass = 'yellow';
		}
		// If current user is the winner
		else if(currentUser.id == winner.id) {
			html = "<u>Result</u>: You won";
			resultClass = 'green';
		}
		// The user participated in the game but is not the winner
		else if((currentUser.id == opponent.id) || (currentUser.id == creator.id)) {
			html = "<u>Result</u>: You lost"
			resultClass = 'red';
		}
		// The user did not participate in the game
		else {
			html = "<u>Result</u>: '"+winner.username+"' won";
			resultClass = 'green';
		}
		$('#result').html(html);
		$('#result-div').addClass(resultClass);

		if(winner != null) {
			if(winner.id == creator.id) {
				$('#creator').addClass('green');
				$('#opponent').addClass('red');
			}
			else {
				$('#opponent').addClass('green');
				$('#creator').addClass('red');
			}
		}

		// If game has completed and the user is one of the participants,
		// enable the reset button
		if(currentUser.id == creator.id || currentUser.id == opponent.id) {
			$('#reset').prop("disabled", false);
		}
		else {
			$('#reset').prop("disabled", true);
		}
	}

	displayTurn() {
		let turn = this.state.game.turn;
		let creator = this.state.game.creator;

		$('#reset').prop("disabled", true);
		$('#creator').removeClass('green red yellow');
		$('#opponent').removeClass('green red yellow');
		$('#result-div').removeClass('green red yellow');

		$('#result').html("<u>Result</u>: Ongoing");

		if(turn != null && turn.id == creator.id) {
			$('#creator').addClass('player-turn');
			$('#opponent').removeClass('player-turn');
		}
		else {
			$('#creator').removeClass('player-turn');
			$('#opponent').addClass('player-turn');
		}
	}

	componentDidUpdate(prevProps) {
		// Adding some extra html to django template here
		this.setSymbols();

		if(this.state.game.completed) {
			this.displayResult();
		}
		else {
			this.displayTurn();
		}
	}

	handleData(data) {
		let result = JSON.parse(data)
		this.setState({game:result.game, squares:result.squares})
	}

	isPlayerTurn() {
		let turn = this.state.game.turn
		let currentUser = this.props.currentUser
		let creator = this.state.game.creator
		if(turn != null) {
			return turn.id == currentUser.id
		}
		else {
			// If turn is null, then it's the opponent's turn
			// basically the user that is not the creator
			return currentUser.id != creator.id
		}
	}

	renderBoard() {
		let board = [];
		let currentRow = -1;
		if(this.state.game != null && this.state.squares != null) {

			board = this.state.squares.map((square) => {
				if(square.row != currentRow) {
					// New row
					currentRow = square.row
					let rowCols = this.state.squares.filter((c) => {
						if(c.row === currentRow) {
							return c
						}
					})
					return this.renderRow(currentRow, rowCols)
				}
			}, this);
		}
		else {
			board = <p>LOADING</p>;
		}
		return board;
	}

	render() {
		return (
			<div className="w-100 mb-3">

			{this.renderBoard()}

			<WebSocket ref="socket" url={this.props.socket}
					   onMessage={this.handleData.bind(this)}
					   reconnect={true}/>
			</div>
		)
	}

}

export default ClaimingGameBoard
