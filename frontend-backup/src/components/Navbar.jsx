import React from 'react'
import '../components/Navbar.css'
import {Link} from 'react-router-dom'
import { GiCook } from "react-icons/gi"

function Navbar(){
    return (
        <>
    {/*navigation bar */}
        <nav className="navbar">
            <div className ="logo-icon">
                <GiCook className="cook-icon"/>
                <Link to="/" className="links">
                    Recipe Recommender
                </Link>
            </div>
            <div className="login-signup">
                <Link to="/profile" className="links">Profile  </Link>
                <Link to="/login" className="links">Login/</Link>
                <Link to="/signup" className="links">Sign Up</Link>
            </div>
        </nav>

    </>
    );
}

export default Navbar;