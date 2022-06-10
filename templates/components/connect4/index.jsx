import React from 'react';
import Connect4Board from './Connect4Board.jsx';
import {createRoot} from 'react-dom/client';
import $ from 'jquery';

let current_user = null;
const host = location.host;
const gc = $('#game-component').data('gc');
const socket = 'ws://'+host+'/ws/connect4/'+gc;

$.get('/current-user/?format=json', (result) => {
	current_user = result
	const container = document.getElementById("game-component")
	const root = createRoot(container)
	root.render(
		<Connect4Board currentUser={current_user} gc={gc} socket={socket}/>
	)
})
