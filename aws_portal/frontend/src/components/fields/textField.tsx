import * as React from 'react';
import { Component } from 'react';
import "./textField.css"

interface TextFieldProps {
    id: string
    img: React.ReactElement
    type: string
    placeholder: string
    prefill: string
    label: string
    feedback: string
}
 
interface TextFieldState {
    text: string
}
 
class TextField extends React.Component<TextFieldProps, TextFieldState> {
    state = {
        text:  ''
    }

    render() {
        const { id, img, type, placeholder, prefill, label, feedback } = this.props;

        return (
            <div className="text-field-container">
                { label ? <label className='text-field-label' htmlFor={ id }>{ label }</label> : null }
                <div className="text-field-content">
                    { img ? img : null }
                    <input type={ type ? type : "text" } className="text-field-input" placeholder={ placeholder } defaultValue={ prefill }/>
                </div>
                { feedback ? <span className="text-field-feedback">{ feedback }</span> : null }
            </div>
        );
    }
}
 
export default TextField;