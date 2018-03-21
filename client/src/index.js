import uuidv4 from 'uuid/v4';

let token = '';

function showCreateGameDialog() {
    $('#create-game-dialog').show();
}

function createGame() {
    const gameId = uuidv4();
    const userId = uuidv4();

    const req = {
        gameId, 
        userId
    };

    $.ajax({
        url: '/api/create_game', 
        method: 'GET',
        dataType: 'json',
        data: req,
        success: (data) => {
            token = data.token;
            const gameHashId = data.hash_id;
            console.log(gameHashId);
        }
    });
}

$('#create-game-dialog').hide();
$('#join-game-dialog').hide();
$('#create-game-button').click(() => showCreateGameDialog());
$('#create-game-ok-button').click(() => createGame());
