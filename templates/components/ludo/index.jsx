import React from 'react';
import LudoBoard from './LudoBoard.jsx';
import {createRoot} from 'react-dom/client';
import $ from 'jquery';
import WebSocket from 'react-websocket';

let current_user = null;
const protocol = location.protocol;
const host = location.host;
const gc = $('#game-component').data('gc');
const socketUrl = "ws://"+host+"/ws/ludo/"+gc;

$.get('/current-user/?format=json', (result) => {
    const container = document.getElementById('ludo-board')
    const root = createRoot(container)
    root.render(
        <LudoBoard currentUser={result} gc={gc} socket={socketUrl}/>
    )
})
