# Roboflow coverage report

**108 ingredients**: 51 covered, 21 need review, 36 not covered.

## By category

| Category | Yes | Review | No |
|---|---|---|---|
| Produce | 33 | 2 | 7 |
| Protein | 6 | 7 | 3 |
| Dairy | 4 | 5 | 5 |
| Grains / Starches | 4 | 0 | 6 |
| Canned / Jarred / Packaged | 0 | 4 | 6 |
| Condiments / Sauces | 2 | 1 | 5 |
| Baking / Pantry | 2 | 2 | 4 |

## Not covered (hand-label or find another dataset)

- **Produce**: Jalapeño [Discrete], Zucchini [Discrete], Plum [Discrete], Squash (butternut/acorn) [Discrete], Kale [Bulk], Shredded Carrots [Bulk], Fresh Basil [Bulk]
- **Protein**: Salmon Fillet [Discrete], Steak [Discrete], Deli Meat (sliced, stacked) [Bulk]
- **Dairy**: Egg Carton [Discrete], Shredded Cheese [Bulk], Cottage Cheese [Bulk], Parmesan (grated) [Bulk], Half & Half [Bulk]
- **Grains / Starches**: Pasta (dry) [Bulk], Oats [Bulk], Cereal [Bulk], Quinoa [Bulk], Couscous [Bulk], Bread Crumbs [Bulk]
- **Canned / Jarred / Packaged**: Canned Tomatoes [Discrete], Canned Corn [Discrete], Canned Soup [Discrete], Jar of Pasta Sauce [Discrete], Jar of Salsa [Discrete], Mayo Jar [Discrete]
- **Condiments / Sauces**: Vinegar [Bulk], Hot Sauce [Bulk], BBQ Sauce [Bulk], Honey [Bulk], Maple Syrup [Bulk]
- **Baking / Pantry**: Brown Sugar [Bulk], Baking Powder [Bulk], Baking Soda [Bulk], Vanilla Extract [Bulk]

## Needs review (decide the mapping by hand)

- Green Beans [Bulk]  <-  food-ingredients:Beans, ingredients:bean, ingredients:beans
- Cherry Tomatoes [Bulk]  <-  ingredients:cherry
- Chicken Drumstick [Discrete]  <-  food-ingredients:Chicken, ingredients:chicken
- Bacon Slice [Discrete]  <-  food-ingredients:Bacon, ingredients:bacon
- Pork Chop [Discrete]  <-  food-ingredients:Pork, ingredients:pork
- Ground Turkey [Bulk]  <-  ingredients:turkey
- Tofu Block [Bulk]  <-  food-ingredients:Tofu, ingredients:tofu
- Canned Tuna [Bulk]  <-  ingredients:tuna
- Canned Beans [Bulk]  <-  food-ingredients:Beans, ingredients:bean, ingredients:beans
- Cheese Block [Discrete]  <-  food-ingredients:Cheese, ingredients:cheese
- Sliced Cheese [Discrete]  <-  food-ingredients:Cheese, ingredients:cheese
- Cream Cheese [Bulk]  <-  food-ingredients:Cheese, ingredients:cheese, ingredients:cream
- Heavy Cream [Bulk]  <-  ingredients:cream
- String Cheese [Discrete]  <-  food-ingredients:Cheese, ingredients:cheese
- Jar of Peanut Butter [Discrete]  <-  ingredients:peanut
- Jar of Jam [Discrete]  <-  ingredients:jam
- Ketchup Bottle [Discrete]  <-  food-ingredients:Ketchup, ingredients:ketchup
- Mustard Bottle [Discrete]  <-  ingredients:mustard
- Vegetable Oil [Bulk]  <-  ingredients:oil
- Black Pepper [Bulk]  <-  ingredients:pepper
- Chocolate Chips [Bulk]  <-  ingredients:chocolate

## Covered but thin (< 100 instances)

- Fresh Cilantro/Parsley [Bulk]: 2 instances
- Tortillas (stack) [Bulk]: 2 instances
- Kiwi [Discrete]: 13 instances
- Olive Oil [Bulk]: 18 instances
- Ground Beef [Bulk]: 19 instances
- Soy Sauce [Bulk]: 26 instances
- Sour Cream [Bulk]: 32 instances
- Salt [Bulk]: 41 instances

## Duplicate source classes that map to one ingredient (merge them)

- food-ingredients: Garden Peas, Green Peas, Pea  ->  Peas
- ingredients: blueberry, strawberry  ->  Berries (strawberries/blueberries)
- ingredients: egg, eggs  ->  Egg
- ingredients: onion, spring onion  ->  Onion

## Largest source classes not on your list (candidates to add)

- fvd: 0 (43155)
- food-ingredients: Chili Pepper -Khursani- (1268)
- ingredients: pork belly (857)
- ingredients: cashew (745)
- ingredients: meatball (721)
- food-ingredients: Taro Leaves -Karkalo- (665)
- ingredients: ham (634)
- food-ingredients: Stinging Nettle -Sisnu- (472)
- food-ingredients: Green Mint -Pudina- (466)
- food-ingredients: Taro Root-Pidalu- (461)
- food-ingredients: Turnip (454)
- food-ingredients: Bitter Gourd (452)
- food-ingredients: Snake Gourd -Chichindo- (438)
- food-ingredients: Fiddlehead Ferns -Niguro- (425)
- food-ingredients: Pointed Gourd -Chuche Karela- (421)
- food-ingredients: Palungo -Nepali Spinach- (360)
- food-ingredients: Bottle Gourd -Lauka- (355)
- ingredients: chilli (343)
- ingredients: bok choy (338)
- food-ingredients: Onion Leaves (317)
- food-ingredients: Masyaura (293)
- food-ingredients: Sponge Gourd -Ghiraula- (293)
- ingredients: pineapple (267)
- food-ingredients: Chayote-iskus- (265)
- food-ingredients: Bamboo Shoots -Tama- (261)
- food-ingredients: Okra -Bhindi- (260)
- food-ingredients: Red Lentils (255)
- food-ingredients: Lapsi -Nepali Hog Plum- (251)
- food-ingredients: Rayo ko Saag (250)
- food-ingredients: Artichoke (230)
- ingredients: coconut (226)
- food-ingredients: Cinnamon (212)
- food-ingredients: Asparagus -Kurilo- (210)
- food-ingredients: Akabare Khursani (206)
- food-ingredients: Broad Beans -Bakullo- (204)
- food-ingredients: Gundruk (201)
- food-ingredients: Rice -Chamal- (197)
- ingredients: chicken wing (197)
- ingredients: melon (196)
- ingredients: pumpkin (195)
