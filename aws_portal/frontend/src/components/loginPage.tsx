import * as React from 'react';
import { Component } from 'react';
import "./loginPage.css"
import TextField from "./fields/textField"

interface LoginPageProps {}
 
interface LoginPageState {}
 
class LoginPage extends React.Component<LoginPageProps, LoginPageState> {
    // state = { :  }
    render() { 
        return (
            <div className="login-container">
                <div className='login-image-container'>
                    <div className='login-image'>Image placeholder</div>
                </div>
                <div className="login-menu">
                    <div className="login-menu-content">
                        <h1>Geriatric Sleep Research Lab</h1>
                        <h2>AWS Data Portal</h2>
                        <TextField
                            id="login-email"
                            placeholder="Email"
                            prefill=""
                            label=""
                            feedback="Invalid email address"
                        />
                        <span>Password field</span>
                        <div className="flex flex-space-between">
                            <span>Login button</span>
                            <span>Forgot password?</span>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}
 
export default LoginPage;
