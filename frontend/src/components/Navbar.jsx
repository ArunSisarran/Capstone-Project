import React from 'react'
import '../css/Navbar.css'
import {Link,useNavigate} from 'react-router-dom'
import { GiCook } from "react-icons/gi"
import {useAuth} from '../context/AuthContext'

function Navbar(){
    const {user, isLoggedIn, logout} = useAuth();

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
                    <Link to="/profile" className="links">My Profile  </Link>
                    <button onClick= {logout}>Log out</button>
                    </div>
                ):(
                    <>
                <Link to="/profile" className="links">Profile  </Link>
                <Link to="/login" className="links">Login/</Link>
                <Link to="/signup" className="links">Sign Up</Link>
                </>
                )}
            </div>
        </nav>

    </>
    );
}

export default Navbar;