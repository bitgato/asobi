import React from 'react';
import {createRoot} from 'react-dom/client';
import $ from 'jquery';
import BattleshipWrapper from './BattleshipWrapper.jsx';

var current_user = null;
const host = location.host;
const gc = $('#game-component').data('gc');
const socketUrl = 'wss://'+host+'/ws/battleship/'+gc;

$.get('/current-user/?format=json', (result) => {
    current_user = result
    const container = document.getElementById("game-component")
    const root = createRoot(container)
    root.render(
        <BattleshipWrapper currentUser={current_user} socketUrl={socketUrl} gc={gc}/>
    )
})
