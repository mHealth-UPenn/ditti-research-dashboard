import * as React from 'react';
import { Component } from 'react';

interface LoginPageProps {}
 
interface LoginPageState {}
 
class LoginPage extends React.Component<LoginPageProps, LoginPageState> {
    // state = { :  }
    render() { 
        return (
            <div className="login-container">
                <div className='login-image'>Image placeholder</div>
                <div className="login-menu">
                    <div className="login-menu-content">
                        <h1>Geriatric Sleep Research Lab</h1>
                        <h2>AWS Data Portal</h2>
                        <span>Email field</span>
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
