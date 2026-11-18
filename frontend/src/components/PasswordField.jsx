import {useState} from 'react'
import TextField from '@mui/material/TextField';
import InputAdornment from '@mui/material/InputAdornment';
import IconButton from '@mui/material/IconButton';
import VisibilityRounded from '@mui/icons-material/VisibilityRounded';
import VisibilityOffRounded from '@mui/icons-material/VisibilityOffRounded';

function PasswordField(props){
    const [show, setShow] = useState(false);
    return (
        <TextField {...props} type={show ? "text" : "password"} fullWidth
            slotProps={{input: {endAdornment: (
                <InputAdornment position="end">
                    <IconButton onClick={() => setShow(!show)} edge="end" aria-label={show ? "Hide password" : "Show password"}>
                        {show ? <VisibilityOffRounded/> : <VisibilityRounded/>}
                    </IconButton>
                </InputAdornment>
            )}}}/>
    );
}

export default PasswordField;
