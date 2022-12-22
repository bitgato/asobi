import React, {Component} from 'react'
import ReactDOM from 'react-dom'
import PropTypes from 'prop-types'
import clsx from 'clsx'

class ClaimingGameSquare extends Component {

    constructor(props) {
        super(props)
        this.state = {
            disabled: false
        }
        this.squareClicked = this.squareClicked.bind(this)
        this.resize = this.resize.bind(this)
    }

    resize() {
        var $this = $(ReactDOM.findDOMNode(this))
        let width = $this.width()
        $this.height(width)
    }

    componentDidMount() {
        window.addEventListener('resize', this.resize)
        this.resize()
    }

    takeOwnership() {
        this.props.sendSocketMessage({
            action: "claim_square",
            square_id: this.props.squareId
        })
    }

    squareClicked(square) {
        this.setState({disabled: true});
        if(this.isAvailable()) {
            this.takeOwnership()
        }
    }

}

export default ClaimingGameSquare
