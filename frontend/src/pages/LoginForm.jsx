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
import {logInWith, SERVER_DOWN} from '../utils/auth.js'
import '../css/Login-SignupForm.css'

function Login(){
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
                    <Typography variant="h1">Log in</Typography>
                    <Typography color="text.secondary">Welcome back. Your saved recipes are waiting.</Typography>
                </header>

                <form className="auth-form" noValidate onSubmit={handleSubmit(onSubmit)}>
                    <TextField label="Email" type="email" autoComplete="email" fullWidth
                        {...field("email", {
                            required: "Enter your email",
                            pattern: {value: /^\S+@\S+\.\S+$/, message: "Enter a valid email, like you@example.com"},
                        })}/>
                    <PasswordField label="Password" autoComplete="current-password"
                        {...field("password", {required: "Enter your password"})}/>
                    {error && <Alert severity="error" role="alert">{error}</Alert>}
                    <Button type="submit" size="large" fullWidth disabled={isSubmitting}
                            endIcon={isSubmitting ? <CircularProgress size={18} color="inherit"/> : null}>
                        Log in
                    </Button>
                </form>

                <p className="auth-card__alt">New here? <Link to="/signup">Create an account</Link></p>
            </div>
        </main>
    );
}

export default Login;
