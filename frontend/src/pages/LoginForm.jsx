import React from 'react'
import {useState} from 'react'
import PersonIcon from '@mui/icons-material/Person';
import EmailIcon from '@mui/icons-material/Email';
import LockIcon from '@mui/icons-material/Lock';
import '../pages/Login-SignupForm.css'
import '../components/Navbar'
import {Link} from 'react-router-dom'
import {useNavigate} from 'react-router-dom';

function Login(){
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate();

    const handleEmailChange = (e) => setEmail(e.target.value);
    const handlePasswordChange = (e) => setPassword(e.target.value);

    const handleSubmit = (e) => {
        e.preventDefault();

        if(!email.trim() || !password){
            alert("please enter your email and password");
            return;
        }

        console.log(email,password);
    }



    return(
    <div className="page">
        <div className="container">

            <h1>Login</h1>

            <form onSubmit={handleSubmit}>

                <div className="inputs">
                    <input 
                        type = "email" 
                        placeholder="Email Address" 
                        value = {email} 
                        onChange={handleEmailChange} 
                        required
                    />
                    <EmailIcon className="icons" />
                </div>

                <div className="inputs">
                    <input 
                        type = "password" 
                        placeholder="Password"
                        value = {password}
                        onChange={handlePasswordChange}
                        required
                    />
                    <LockIcon className="icons" />
                </div>


                <div className="remember">
                    <label><input type="checkbox" />Remember me</label>
                </div>

                <div className="submit-container">
                    <button type="submit">Login</button>
                </div>

                <div className="login-register">
                    <p>Don't have an account? {""}
                        <Link to="/signup">Sign Up</Link>
                    </p>
                    <br></br>
                    <a href="#"> Forget Password </a>
                </div>

            </form>

        </div>
    </div>
    );
} 

export default Login;