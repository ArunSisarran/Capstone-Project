import SavedRecipes from './SavedRecipes'

function FavoritePage({favorites, setFavorites, savedforlater, setSavedForLater}){
    return <SavedRecipes kind="favorite" list={favorites} setList={setFavorites}
                         favorites={favorites} setFavorites={setFavorites}
                         savedforlater={savedforlater} setSavedForLater={setSavedForLater}/>;
}

export default FavoritePage;
