import {Link, useLocation} from 'react-router-dom'
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import {useAuth} from '../context/AuthContext'
import '../css/Profile.css'

const TABS = [
    {label: "History", to: "/profile"},
    {label: "Favorites", to: "/favorite"},
    {label: "Saved", to: "/savedforlater"},
];

function AccountLayout({children}){
    const {user, isLoggedIn, loading} = useAuth();
    const {pathname} = useLocation();
    const email = user?.email || "";

    return (
        <main className="page-shell account-page">
            <header className="panel account-page__header">
                <span className="account-page__avatar" aria-hidden="true">{(email[0] || "?").toUpperCase()}</span>
                <div className="account-page__who">
                    <Typography variant="h1">Your account</Typography>
                    <Typography variant="meta" component="p">
                        {isLoggedIn ? email : loading ? "" : "Log in to keep favorites and saved recipes."}
                    </Typography>
                </div>
                <div className="account-page__actions">
                    {isLoggedIn ? (
                        <Button variant="outlined" component={Link} to="/changepassword">Change password</Button>
                    ) : !loading && (
                        <Button component={Link} to="/login">Log in</Button>
                    )}
                </div>
            </header>

            <Tabs value={TABS.some((t) => t.to === pathname) ? pathname : false}
                  variant="scrollable" allowScrollButtonsMobile aria-label="Account sections" className="account-page__tabs">
                {TABS.map((t) => <Tab key={t.to} label={t.label} value={t.to} component={Link} to={t.to}/>)}
            </Tabs>

            {children}
        </main>
    );
}

export default AccountLayout;
