import $ from 'jquery';
import clsx from 'clsx';
import PropTypes from 'prop-types';
import React, {Component} from 'react';
import WebSocket from 'react-websocket';
import LudoPiece from './LudoPiece.jsx';

class LudoBoard extends Component {

	constructor(props) {
		super(props);
		this.state = {
			game: null,
			player: null,
			pieces: null,
			currentPlayer: null,
			turnPlayer: null
		};
		this.sendSocketMessage = this.sendSocketMessage.bind(this);
		this.getColor = this.getColor.bind(this);
	}

	getColor(playerNumber) {
        switch(playerNumber) {
            case 0: return "dark-red";
            case 1: return "dark-green";
            case 2: return "dark-yellow";
            case 3: return "dark-blue";
        }
    }

    findPlayers(players, game) {
    	var result = [];
		var currentPlayer = null;
		var turnPlayer = null;
		let id = this.props.currentUser.id;
		players.some((player, i) => {
			if(player.user.id == id) {
				currentPlayer = player;
			}
			if(player.player_number == game.turn) {
				turnPlayer = player;
			}
			return (currentPlayer != null) && (turnPlayer != null);
		});
		result.push(currentPlayer);
		result.push(turnPlayer);
		return result;
    }

	componentDidMount() {
		const gameUrl = location.protocol+'//'+location.host+'/ludo-from-code/'+this.props.gc;
		this.serverRequest = $.get(gameUrl, (result) => {
			let players = this.findPlayers(result.players, result.game);
			let currentPlayer = players[0];
			let turnPlayer = players[1];
			this.setState({
				game: result.game,
				players: result.players,
				pieces: result.pieces,
				currentPlayer: currentPlayer,
				turnPlayer: turnPlayer
			});
			this.displayResult(currentPlayer, turnPlayer, result);
		})
		$('#dice-roll').click(() => {
			$('#dice-roll').prop("disabled", true);
			let message = {
				'action': 'roll',
				'player_id': this.state.currentPlayer.id
			}
			this.sendSocketMessage(message);
		})
		$('#reset').click(() => {
			let message = {
				'action': 'reset'
			};
			this.sendSocketMessage(message);
		});
	}

	displayPlayer(player=null, playerIndex) {
		let username = "---";
		let playerNumber = playerIndex;
		let piecesFinished = 0;
		let html = null;
		if(player != null) {
			username = player.user.username;
			playerNumber = player.player_number;
			piecesFinished = player.pieces_finished;
			if(player.position > 0) {
				let medal = null;
				switch(player.position) {
					case 1: medal = "gold"; break;
					case 2: medal = "silver"; break;
					case 3: medal = "bronze"; break;
				}
				let className = clsx(
					medal,
					'me-2'
				);
				html = "<div class='"+className+"'></div>"+username;
			}
		}
		if(html == null) {
			html = '('+piecesFinished+') '+username;
		}
		$('#player'+playerNumber).html(html);
		if(playerNumber == this.state.game.turn) {
			$('#player'+playerNumber+"-back").addClass('player-turn');
		}
		else {
			$('#player'+playerNumber+"-back").removeClass('player-turn');
		}
	}

	setDice(number) {
		$("#dice").removeClass((index, className) => {
			return (className.match (/(^|\s)dice-\S+/g) || []).join(' ');
		})
		$('#dice').addClass('dice-'+number);
	}

	rollDice(finalNumber, playerId) {
		let onDice = 1;
		let loopCount = 1;
		let interval = setInterval(() => {
			this.setDice(onDice);
			if(loopCount > 2) {
				this.setDice(finalNumber);
				clearInterval(interval);
			}
			onDice++;
			if(onDice > 6) {
				onDice = 1;
				loopCount++;
			}
		}, 100);
		if(this.state.currentPlayer != null && playerId == this.state.currentPlayer.id) {
			let message = {
				'action': 'rolled',
				'player_id': playerId
			};
			this.sendSocketMessage(message);
		}
	}

	componentDidUpdate(prevProps) {
		let playerCount = 0;
		this.state.players.forEach((player, i) => {
			this.displayPlayer(player, i);
			playerCount++;
		});
		while(playerCount < 4) {
			this.displayPlayer(null, playerCount);
			playerCount++;
		}
	}

	componentWillUnmount() {
		this.serverRequest.abort();
	}

	sendSocketMessage(message) {
		const socket = this.refs.socket;
		socket.state.ws.send(JSON.stringify(message));
	}

    sendSocketMessage(message) {
        const socket = this.refs.socket;
        socket.state.ws.send(JSON.stringify(message));
    }

    displayResult(currentPlayer, turnPlayer, result) {
    	if(result.game.completed) {
    		$('#result').html("Game over");
    		$('#dice-roll').prop("disabled", true);
    		$('#reset').prop("disabled", false);
    		return;
    	}
    	else {
			$('#reset').prop('disabled', true);
    	}
    	let html = null;
    	let status = null;
    	if(currentPlayer.id != turnPlayer.id) {
    		status = turnPlayer.status.toLowerCase();
    		if(status != 'moving') {
    			html = "'"+turnPlayer.user.username+"' is "+status;
    		}
    	}
    	else {
    		status = currentPlayer.status.toLowerCase();
    		if(status != 'moving') {
    			html = "Your turn for "+status;
    		}
    		else {
    			html = "You are moving";
    		}
    	}
    	$('#result').html(html);
    	this.handleCurrentPlayer(currentPlayer);
    }

    handleCurrentPlayer(currentPlayer, turnPlayer) {
    	if(currentPlayer.status == 'Rolling') {
			$('#dice-roll').prop("disabled", false);
		}
		else if(currentPlayer.status == 'Moving') {
			$('#dice-roll').prop("disabled", true);
			let message = {
				'action': 'move'
			}
			let i = 0;
			// Send message after 100 milliseconds
			let interval = setInterval(() => {
				if(i == 1) {
					clearInterval(interval);
					this.sendSocketMessage(message);
				}
				i++;
			}, 100);
		}
		else {
			$('#dice-roll').prop("disabled", true);
			this.setDice(currentPlayer.roll);
		}
    }

	handleData(data) {
		let result = JSON.parse(data);
		if(result.roll != undefined) {
			this.rollDice(result.roll, result.player_id);
		}
		else {
			let players = this.findPlayers(result.players, result.game);
			let currentPlayer = players[0];
			let turnPlayer = players[1];
			this.setState({
				game: result.game,
				players: result.players,
				pieces: result.pieces,
				currentPlayer: currentPlayer,
				turnPlayer: turnPlayer
			});
			this.displayResult(currentPlayer, turnPlayer, result);
		}
	}

	render() {
		let board = "";
		let currentPlayerNumber = -1;
		if(this.state.currentPlayer != null) {
			currentPlayerNumber = this.state.currentPlayer.player_number;
		}
		if(currentPlayerNumber < 0) {
			$('#reset').prop("disabled", true);
		}
		if(this.state.game != null && this.state.pieces != null) {

			board = this.state.pieces.map((piece) => {
				return <LudoPiece	key={piece.id}
									pieceId={piece.id}
									position={piece.position}
									pieceNumber={piece.piece_number}
									player={piece.player}
									currentUserId={this.props.currentUser.id}
									currentPlayerNumber={currentPlayerNumber}
									canMove={piece.can_move}
									finished={piece.finished}
									gameCompleted={this.state.game.completed}
									sendSocketMessage={this.sendSocketMessage}
									getColor={this.getColor}
									/>;
			}, this);
		}
		return (
			<div>
			{board}
			<WebSocket ref="socket" url={this.props.socket}
					   onMessage={this.handleData.bind(this)}
					   reconnect={true}/>
			</div>
		);
	}

}

LudoBoard.propTypes = {
	gc: PropTypes.string,
	socket: PropTypes.string,
	currentUser: PropTypes.object
};


export default LudoBoard;
