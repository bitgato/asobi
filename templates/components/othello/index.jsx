import React from 'react';
import OthelloBoard from './OthelloBoard.jsx';
import {createRoot} from 'react-dom/client';
import $ from 'jquery';

let current_user = null;
const host = location.host;
const gc = $('#game-component').data('gc');
const socket = 'wss://'+host+'/ws/othello/'+gc;

$.get('/current-user/?format=json', (result) => {
	current_user = result
	const container = document.getElementById("game-component")
	const root = createRoot(container)
	root.render(
		<OthelloBoard currentUser={current_user} gc={gc} socket={socket}/>
	)
})
