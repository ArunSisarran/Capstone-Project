import {useState} from 'react'
import {Link} from 'react-router-dom'
import {useForm} from 'react-hook-form'
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import PasswordField from '../components/PasswordField'
import {useAuth} from '../context/AuthContext'
import {base_url} from '../api/api.js'
import {errorText, SERVER_DOWN} from '../utils/auth.js'
import '../css/Login-SignupForm.css'

function ChangeEmail(){
    const {register, handleSubmit, reset, formState: {errors, isSubmitting}} = useForm();
    const {user, login} = useAuth();
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    const field = (name, rules) => {
        const {ref, ...rest} = register(name, rules);
        return {...rest, inputRef: ref, error: Boolean(errors[name]), helperText: errors[name]?.message};
    };

    const onSubmit = async ({email, current_password}) => {
        setError("");
        setSuccess("");
        const token = localStorage.getItem("token");
        try{
            const response = await fetch(`${base_url}/users/me`, {
                method: "PATCH",
                headers: {"Content-Type": "application/json", Authorization: `Bearer ${token}`},
                body: JSON.stringify({email, current_password}),
            });
            const data = await response.json().catch(() => null);
            if (!response.ok){
                throw new Error(errorText(data, "Couldn't update your email. Try again."));
            }
            // refresh the stored user so the navbar and account page show the new email -Arun
            login(data, token);
            reset();
            setSuccess(`Your email is now ${data.email}.`);
        }catch(err){
            setError(err instanceof TypeError ? SERVER_DOWN : err.message);
        }
    };

    return(
        <main className="auth-page">
            <div className="auth-card">
                <header className="auth-card__head">
                    <Typography variant="h1">Change email</Typography>
                    <Typography color="text.secondary">
                        {user?.email ? `You log in with ${user.email}. ` : ""}Enter the new email and your password to confirm.
                    </Typography>
                </header>

                <form className="auth-form" noValidate onSubmit={handleSubmit(onSubmit)}>
                    <TextField label="New email" type="email" autoComplete="email" fullWidth
                        {...field("email", {
                            required: "Enter your new email",
                            pattern: {value: /^\S+@\S+\.\S+$/, message: "Enter a valid email, like you@example.com"},
                            validate: (value) => value.trim().toLowerCase() !== (user?.email || "").toLowerCase() || "That's already your email",
                        })}/>
                    <PasswordField label="Current password" autoComplete="current-password"
                        {...field("current_password", {required: "Enter your current password"})}/>
                    {error && <Alert severity="error" role="alert">{error}</Alert>}
                    {success && <Alert severity="success">{success}</Alert>}
                    <Button type="submit" size="large" fullWidth disabled={isSubmitting}
                            endIcon={isSubmitting ? <CircularProgress size={18} color="inherit"/> : null}>
                        Update email
                    </Button>
                </form>

                <p className="auth-card__alt"><Link to="/profile">Back to your account</Link></p>
            </div>
        </main>
    );
}

export default ChangeEmail;
