import Typography from '@mui/material/Typography';

function EmptyState({icon, title, text, action}){
    return (
        <div className="empty-state">
            <span className="empty-state__icon">{icon}</span>
            <Typography variant="h2">{title}</Typography>
            <Typography color="text.secondary">{text}</Typography>
            {action}
        </div>
    );
}

export default EmptyState;
