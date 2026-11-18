import {useState} from 'react'
import {Link, NavLink, useLocation, useNavigate} from 'react-router-dom'
import Button from '@mui/material/Button'
import Menu from '@mui/material/Menu'
import MenuItem from '@mui/material/MenuItem'
import Divider from '@mui/material/Divider'
import BottomNavigation from '@mui/material/BottomNavigation'
import BottomNavigationAction from '@mui/material/BottomNavigationAction'
import PhotoCameraRounded from '@mui/icons-material/PhotoCameraRounded'
import MenuBookRounded from '@mui/icons-material/MenuBookRounded'
import BookmarkRounded from '@mui/icons-material/BookmarkRounded'
import PersonRounded from '@mui/icons-material/PersonRounded'
import ExpandMoreRounded from '@mui/icons-material/ExpandMoreRounded'
import '../css/Navbar.css'
import {useAuth} from '../context/AuthContext'

const tabFor = (path) =>
    path === "/" ? "scan"
    : path.startsWith("/result") ? "recipes"
    : path.startsWith("/savedforlater") || path.startsWith("/favorite") ? "saved"
    : path.startsWith("/profile") || path.startsWith("/changepassword") ? "profile"
    : false;

function Navbar(){
    const {loading, logout, isLoggedIn} = useAuth();
    const {pathname} = useLocation();
    const navigate = useNavigate();
    const [menuAnchor, setMenuAnchor] = useState(null);

    const go = (path) => { setMenuAnchor(null); navigate(path); };
    const handleLogout = () => { setMenuAnchor(null); logout(); navigate("/"); };

    return (
        <>
        <header className="topbar">
            <Link to="/" className="brand" aria-label="Recipe Recommender home">
                <span className="brand__mark" aria-hidden="true"><PhotoCameraRounded fontSize="inherit"/></span>
                <span className="brand__name">Recipe Recommender</span>
            </Link>

            <nav className="topnav" aria-label="Main">
                <NavLink to="/" end className="topnav__link">Scan</NavLink>
                <NavLink to="/result" className="topnav__link">Recipes</NavLink>
                <NavLink to="/favorite" className="topnav__link">Favorites</NavLink>
            </nav>

            {/* account area stays empty until login status is known -Arun */}
            <div className="account">
                {loading ? null : isLoggedIn ? (
                    <>
                        <Button variant="outlined" className="account__menu-button"
                                startIcon={<PersonRounded/>} endIcon={<ExpandMoreRounded/>}
                                aria-haspopup="menu" aria-expanded={Boolean(menuAnchor)}
                                onClick={(e) => setMenuAnchor(e.currentTarget)}>
                            Account
                        </Button>
                        <Menu anchorEl={menuAnchor} open={Boolean(menuAnchor)} onClose={() => setMenuAnchor(null)}
                              anchorOrigin={{vertical: "bottom", horizontal: "right"}}
                              transformOrigin={{vertical: "top", horizontal: "right"}}
                              slotProps={{paper: {sx: {mt: 1, minWidth: 200}}}}>
                            <MenuItem onClick={() => go("/profile")}>Profile</MenuItem>
                            <MenuItem onClick={() => go("/favorite")}>Favorites</MenuItem>
                            <MenuItem onClick={() => go("/savedforlater")}>Saved for later</MenuItem>
                            <MenuItem onClick={() => go("/changepassword")}>Change password</MenuItem>
                            <Divider/>
                            <MenuItem onClick={handleLogout}>Log out</MenuItem>
                        </Menu>
                    </>
                ) : (
                    <>
                        <Link to="/login" className="account__login">Log in</Link>
                        <Button component={Link} to="/signup" variant="outlined" className="account__signup">Sign up</Button>
                    </>
                )}
            </div>
        </header>

        <nav className="bottomnav" aria-label="Main">
            <BottomNavigation showLabels value={tabFor(pathname)}>
                <BottomNavigationAction value="scan" label="Scan" icon={<PhotoCameraRounded/>} component={Link} to="/"/>
                <BottomNavigationAction value="recipes" label="Recipes" icon={<MenuBookRounded/>} component={Link} to="/result"/>
                <BottomNavigationAction value="saved" label="Saved" icon={<BookmarkRounded/>} component={Link} to="/savedforlater"/>
                <BottomNavigationAction value="profile" label="Profile" icon={<PersonRounded/>} component={Link} to="/profile"/>
            </BottomNavigation>
        </nav>
        </>
    );
}

export default Navbar;
