import {useState} from 'react'
import {Link, useNavigate} from 'react-router-dom'
import {useForm} from 'react-hook-form'
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import PasswordField from '../components/PasswordField'
import {useAuth} from '../context/AuthContext'
import {base_url} from '../api/api.js'
import {errorText, logInWith, SERVER_DOWN} from '../utils/auth.js'
import '../css/Login-SignupForm.css'

function Signup(){
    const {register, handleSubmit, formState: {errors, isSubmitting}} = useForm();
    const {login} = useAuth();
    const navigate = useNavigate();
    const [error, setError] = useState("");

    const field = (name, rules) => {
        const {ref, ...rest} = register(name, rules);
        return {...rest, inputRef: ref, error: Boolean(errors[name]), helperText: errors[name]?.message};
    };

    const onSubmit = async ({email, password}) => {
        setError("");
        try{
            const response = await fetch(`${base_url}/auth/signup`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({email, password}),
            });
            if (!response.ok){
                throw new Error(errorText(await response.json().catch(() => null), "Couldn't create your account. Try again."));
            }
            const {token, user} = await logInWith(email, password);
            login(user, token);
            navigate("/");
        }catch(err){
            setError(err instanceof TypeError ? SERVER_DOWN : err.message);
        }
    };

    return(
        <main className="auth-page">
            <div className="auth-card">
                <header className="auth-card__head">
                    <Typography variant="h1">Create an account</Typography>
                    <Typography color="text.secondary">Save recipes you love and find them again on any device.</Typography>
                </header>

                <form className="auth-form" noValidate onSubmit={handleSubmit(onSubmit)}>
                    <TextField label="Email" type="email" autoComplete="email" fullWidth
                        {...field("email", {
                            required: "Enter your email",
                            pattern: {value: /^\S+@\S+\.\S+$/, message: "Enter a valid email, like you@example.com"},
                        })}/>
                    {/* backend requires 12+ characters -Arun */}
                    <PasswordField label="Password" autoComplete="new-password"
                        {...field("password", {
                            required: "Choose a password",
                            minLength: {value: 12, message: "Use at least 12 characters"},
                        })}
                        helperText={errors.password?.message || "At least 12 characters"}/>
                    {error && <Alert severity="error" role="alert">{error}</Alert>}
                    <Button type="submit" size="large" fullWidth disabled={isSubmitting}
                            endIcon={isSubmitting ? <CircularProgress size={18} color="inherit"/> : null}>
                        Create account
                    </Button>
                </form>

                <p className="auth-card__alt">Already have an account? <Link to="/login">Log in</Link></p>
            </div>
        </main>
    );
}

export default Signup;
