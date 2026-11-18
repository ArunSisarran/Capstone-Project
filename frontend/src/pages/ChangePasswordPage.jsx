import {useState} from 'react'
import {Link} from 'react-router-dom'
import {useForm} from 'react-hook-form'
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import PasswordField from '../components/PasswordField'
import {base_url} from '../api/api.js'
import {errorText, SERVER_DOWN} from '../utils/auth.js'
import '../css/Login-SignupForm.css'

function ChangePassword(){
    const {register, handleSubmit, reset, formState: {errors, isSubmitting}} = useForm();
    const [error, setError] = useState("");
    const [success, setSuccess] = useState(false);

    const field = (name, rules) => {
        const {ref, ...rest} = register(name, rules);
        return {...rest, inputRef: ref, error: Boolean(errors[name]), helperText: errors[name]?.message};
    };

    // backend replies 204 with no body -Arun
    const onSubmit = async ({current_password, new_password}) => {
        setError("");
        setSuccess(false);
        try{
            const response = await fetch(`${base_url}/users/me/password`, {
                method: "PUT",
                headers: {"Content-Type": "application/json", Authorization: `Bearer ${localStorage.getItem("token")}`},
                body: JSON.stringify({current_password, new_password}),
            });
            if (!response.ok){
                throw new Error(errorText(await response.json().catch(() => null), "Couldn't update your password. Try again."));
            }
            reset();
            setSuccess(true);
        }catch(err){
            setError(err instanceof TypeError ? SERVER_DOWN : err.message);
        }
    };

    return(
        <main className="auth-page">
            <div className="auth-card">
                <header className="auth-card__head">
                    <Typography variant="h1">Change password</Typography>
                    <Typography color="text.secondary">Enter your current password, then choose a new one.</Typography>
                </header>

                <form className="auth-form" noValidate onSubmit={handleSubmit(onSubmit)}>
                    <PasswordField label="Current password" autoComplete="current-password"
                        {...field("current_password", {required: "Enter your current password"})}/>
                    <PasswordField label="New password" autoComplete="new-password"
                        {...field("new_password", {
                            required: "Choose a new password",
                            minLength: {value: 12, message: "Use at least 12 characters"},
                        })}
                        helperText={errors.new_password?.message || "At least 12 characters"}/>
                    {error && <Alert severity="error" role="alert">{error}</Alert>}
                    {success && <Alert severity="success">Your password has been updated.</Alert>}
                    <Button type="submit" size="large" fullWidth disabled={isSubmitting}
                            endIcon={isSubmitting ? <CircularProgress size={18} color="inherit"/> : null}>
                        Update password
                    </Button>
                </form>

                <p className="auth-card__alt"><Link to="/profile">Back to your account</Link></p>
            </div>
        </main>
    );
}

export default ChangePassword;
