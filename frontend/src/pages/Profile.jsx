import {useState} from 'react'
import {Link} from 'react-router-dom'
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import HistoryRounded from '@mui/icons-material/HistoryRounded';
import AccountLayout from '../components/AccountLayout'
import EmptyState from '../components/EmptyState'
import FavoriteButton from '../components/FavoriteButton'
import SavedForLaterButton from '../components/SavedForLaterButton'
import {readHistory, recordView} from '../utils/recordView.js'

const dateFormat = new Intl.DateTimeFormat(undefined, {month: "short", day: "numeric"});

function Profile({favorites, setFavorites, savedforlater, setSavedForLater}){
    const [history] = useState(readHistory);

    if (history.length === 0){
        return (
            <AccountLayout>
                <EmptyState icon={<HistoryRounded fontSize="inherit"/>} title="No recipes viewed yet"
                            text="Recipes you open show up here, so you can find them again."
                            action={<Button component={Link} to="/">Scan your fridge</Button>}/>
            </AccountLayout>
        );
    }

    return (
        <AccountLayout>
            <ul className="panel history-list">
                {history.map((recipe) => (
                    <li key={recipe.id} className="history-list__row">
                        <div className="history-list__text">
                            <Link to={`/result/${recipe.id}`} onClick={() => recordView(recipe)}>{recipe.title}</Link>
                            <Typography variant="meta" component="span">Viewed {dateFormat.format(new Date(recipe.viewedAt))}</Typography>
                        </div>
                        <div className="history-list__actions">
                            <FavoriteButton recipe={recipe} favorites={favorites} setFavorites={setFavorites}/>
                            <SavedForLaterButton recipe={recipe} savedforlater={savedforlater} setSavedForLater={setSavedForLater}/>
                        </div>
                    </li>
                ))}
            </ul>
        </AccountLayout>
    );
}

export default Profile;
