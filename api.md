# Drug Shortage Game Server APIs

## Create Game

### URL

`/api/create_game`

### Method

GET

### URL Parameters:

* userId = [string]

    The unique identifier of the player

* gameId = [string]

    The unique identifier of the game

* numHumanPlayer = [integer]

    The number of human players, ranging from 1 to 6. 

* role = [string]

    What job does the player wants to play. It can be either manufacturer,
    distributor, or health center.

### Success Response

#### Code: 200

Response: 

* token: an authorization token
* hashId: a short ID that can be used for others to join the game.

### Error Response

#### Code: 400 Bad request

This code can be caused by a invalid `numHumanPlayer` field.

## Get Game Parameter

### URL

`/api/get_game_param`

### URL Parameters

* token = [string]

    The authorization token.

* paramName = [string]

    The name of the parameter

### Success Response

#### Code: 200

Response: the parameter value

### Error Response

#### Code: 401 Unauthorized

This happens when the token provided is not valid.

### Code: 400 Bad Request

This happens when the paramName is not supported or the paramName is not 
available for the agent type that the player is controlling.

## Get Game History Parameter

### URL

`/api/get_game_history_param`

### URL Parameters

* token = [string]

    The authorization token.

* paramName = [string]

    The name of the parameter

* cycle = [integer]

    The parameter value to retrieve at a certain cycle

* agentId = [integer]

    The parameter to retrieve about a certain agent

### Success Response

#### Code: 200

Response: the parameter value

### Error Response

### Code: 400 Bad Request

This happens when the paramName is not supported or the paramName is not 
available for the agent type that the player is controlling.

#### Code: 401 Unauthorized

This happens when the token provided is not valid.

#### Code: 404

This happens when the `cycle` provided is not valid. It can be either too 
early that the history has already been forgotten, or the cycle number
if in the future.

Providing an `agentId` that does not map to any agent also causes this error.

## Make a Decision

### URL

`/api/make_decision`

### URL Parameters

* token = [string]

    The authorization token

* decisionName = [string]

    Which decision it is

* decisionValue = [integer]

    The value of the decision. This field should always be a interger.

### Success Response

#### Code: 200

Response: empty

### Error Response

#### Code 400: Bad Request

This happens if the `decisionName` is not supported or the `decisionValue` 
is either not an integer or the is not valid in the game.

#### Code 401: Unauthorized

This happens when the authorization token is not valid

## Next Cycle

### URL

`/api/next_cycle`

### Method

GET

### URL Parameters

* token = [string]

    The authorization token.

### Surccess Response

#### Code: 200

Response: empty

#### Error Response

#### Code: 401 Unauthorized

This happens if the authroization token provided is not valid.
