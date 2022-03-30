import * as React from 'react';
import { Component } from 'react';

interface TextFieldProps {
    id: string
    // badge: React.ReactElement
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
        const { id, placeholder, prefill, label, feedback } = this.props;

        return (
            <div className="text-field-container">
                { label ? <label htmlFor={ id }>label</label> : null }
                <div className="text-field-content">
                    {/* { badge ? badge : null } */}
                    <input type="text" className="text-field-input" placeholder={ placeholder } defaultValue={ prefill }/>
                </div>
                { feedback ? <span className="text-field-feedback">{ feedback }</span> : null }
            </div>
        );
    }
}
 
export default TextField;