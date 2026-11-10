import React from 'react'
import '../css/Navbar.css'
import {Link,useNavigate} from 'react-router-dom'
import { GiCook } from "react-icons/gi"
import {useAuth} from '../context/AuthContext'

function Navbar(){
    const {user, loading, logout,isLoggedIn} = useAuth();

    if(loading) return null;

    return (
        <>
    {/*navigation bar */}
        <nav className="navbar">
            <div className ="logo-icon">
                <Link to="/" className="links">
                    <span>
                    <GiCook className="cook-icon"/>
                    Recipe Recommender
                    </span>
                </Link>
            </div>
            <div className="login-signup">
                {isLoggedIn ? (
                    <div className = "after-login">
                    <p>Welcome!</p>
                    <Link to="/profile" className="links">Account  </Link>
                    <button onClick= {logout}>Log out</button>
                    </div>
                ):(
                    <div className= "account-links">
                <Link to="/login" className="links">Login</Link>
                <Link to="/signup" className="links">Sign Up</Link>
                <Link to="/profile" className="links">Account </Link>
                </div>
                )}
            </div>
        </nav>

    </>
    );
}

export default Navbar;