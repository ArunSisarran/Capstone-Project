import React from 'react'
import '../css/Navbar.css'
import {Link,useNavigate} from 'react-router-dom'
import { GiCook } from "react-icons/gi"

function Navbar({token}){
    const navigate = useNavigate();


    const handleLogout = () => {

        localStorage.removeItem("token");

        console.log("log out work!")


        
        navigate("/")
    }

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
                {token ? (
                    <>
                    <p>Hello!</p>
                    <button onClick= {handleLogout}>Log out</button>
                    </>
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