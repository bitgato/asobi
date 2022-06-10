import React, {Component} from 'react';
import PropTypes from 'prop-types';
import ReactTooltip from 'react-tooltip';

class BattleshipPort extends Component {

    onDrag(ev) {
        ev.dataTransfer.setData('text', ev.target.id)
    }

	render() {
		if(this.props.gameConfirmed) {
			return (
				<div className="ship-port-class">
                    <div className="page-heading">
                        <h2>Ship port</h2>
                    </div>
                    Empty
                </div>
			)
		}
		else {
			return (
			 	<div className="ship-port-class">
                    <div className="page-heading">
                        <h2>Ship port</h2>
                    </div>
                    <div id="ship-port">
                        <div>
                            <img id="carrier"
                                 className="ship-select"
                                 data-tip
                                 data-for="carrier-tip"
                                 data-shipnum="1"
                                 data-shipsleft="1"
                                 draggable="true"
                                 onDragStart={this.onDrag}
                                 src="/static/img/battleship/carrier.png"/>
                            <ReactTooltip id="carrier-tip" place="left" effect="solid">
                                Carrier
                            </ReactTooltip>
                        </div>
                        <div>
                            <img id="battleship"
                                 className="ship-select"
                                 data-tip
                                 data-for="battleship-tip"
                                 data-shipnum="2"
                                 data-shipsleft="1"
                                 draggable="true"
                                 onDragStart={this.onDrag}
                                 src="/static/img/battleship/battleship.png"/>
                            <ReactTooltip id="battleship-tip" place="left" effect="solid">
                                Battleship
                            </ReactTooltip>
                        </div>
                        <div>
                            <img id="cruiser"
                                 className="ship-select"
                                 data-tip
                                 data-for="cruiser-tip"
                                 data-shipnum="3"
                                 data-shipsleft="1"
                                 draggable="true"
                                 onDragStart={this.onDrag}
                                 src="/static/img/battleship/cruiser.png"/>
                            <ReactTooltip id="cruiser-tip" place="left" effect="solid">
                                Cruiser
                            </ReactTooltip>
                        </div>
                        <div>
                            <img id="submarine"
                                 className="ship-select"
                                 data-tip
                                 data-for="submarine-tip"
                                 data-shipnum="4"
                                 data-shipsleft="2"
                                 draggable="true"
                                 onDragStart={this.onDrag}
                                 src="/static/img/battleship/submarine.png"/>
                            <ReactTooltip id="submarine-tip" place="left" effect="solid">
                                Submarine
                            </ReactTooltip>
                        </div>
                        <div>
                            <img id="destroyer"
                                 className="ship-select"
                                 data-tip
                                 data-for="destroyer-tip"
                                 data-shipnum="6"
                                 data-shipsleft="2"
                                 draggable="true"
                                 onDragStart={this.onDrag}
                                 src="/static/img/battleship/destroyer.png"/>
                            <ReactTooltip id="destroyer-tip" place="left" effect="solid">
                                Destroyer
                            </ReactTooltip>
                        </div>
                    </div>
                </div>
            );
		}
	}
}

BattleshipPort.propTypes = {
    gameConfirmed: PropTypes.bool
}

export default BattleshipPort;
