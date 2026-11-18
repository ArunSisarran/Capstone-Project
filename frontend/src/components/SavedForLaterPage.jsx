import SavedRecipes from './SavedRecipes'

function SavedForLaterPage({favorites, setFavorites, savedforlater, setSavedForLater}){
    return <SavedRecipes kind="saved" list={savedforlater} setList={setSavedForLater}
                         favorites={favorites} setFavorites={setFavorites}
                         savedforlater={savedforlater} setSavedForLater={setSavedForLater}/>;
}

export default SavedForLaterPage;
