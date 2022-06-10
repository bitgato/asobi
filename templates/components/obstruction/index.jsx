import React from 'react';
import ObstructionBoard from './ObstructionBoard.jsx';
import {createRoot} from 'react-dom/client';
import $ from 'jquery';

let current_user = null;
const host = location.host;
const gc = $('#game-component').data('gc');
const socket = 'ws://'+host+'/ws/obstruction/'+gc;

$.get('/current-user/?format=json', (result) => {
	current_user = result
	const container = document.getElementById("game-component")
	const root = createRoot(container)
	root.render(
		<ObstructionBoard currentUser={current_user} gc={gc} socket={socket}/>
	)
})
