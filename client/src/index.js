import uuidv4 from 'uuid/v4';

let token = '';
let cycle = 0;

function showCreateGameDialog() {
    $('#create-game-dialog').show();
}

function showJoinGameDialog() {
    $('#join-game-dialog').show();
}

function createGame() {
    const gameId = uuidv4();
    const userId = uuidv4();
    const numHumanPlayer = $('#num-human-player-slide').val();

    const req = {
        gameId, 
        userId,
        numHumanPlayer,
    };

    $.ajax({
        url: '/api/create_game', 
        method: 'GET',
        dataType: 'json',
        data: req,
        success: (data) => {
            token = data.token;
            const gameHashId = data.hash_id;
            startPlayingHealthCenter();
        }
    });
}

function joinGame() {
    console.error('Not implemented');
}

function startPlayingHealthCenter() {
    retrieveHealthCenterInformation();
}

function retrieveParam(cycle, agentId, paramName, dom = null, onSuccess = null) {
    $.ajax({
        url: '/api/get_game_param', 
        method: 'GET',
        dataType: 'json',
        data: {
            token,
            cycle,
            agentId,
            paramName,
        },
        success: (data) => {
            if (dom) {
                dom.html(data);
            }
            if (onSuccess) {
                onSuccess(data);
            }
        },
    });
}

function retrieveHealthCenterInformation() {
    const dom = $(
        `<tr>
            <td>${cycle}</td>
            <td></td>
            <td></td>
            <td></td>
        </tr>`);
    $('#health-center-data-table').append(dom);

    retrieveParam(cycle, 5, 'inventory', dom.children()[1]);
    retrieveParam(cycle, 5, 'urgent', dom.children()[2]);
    retrieveParam(cycle, 5, 'non-urgent', dom.children()[3]);
}

$('#create-game-dialog').hide();
$('#join-game-dialog').hide();
$('#create-game-button').click(() => showCreateGameDialog());
$('#join-game-button').click(() => showJoinGameDialog());
$('#create-game-ok-button').click(() => createGame());
$('#join-game-ok-button').click(() => joinGame());
$('#num-human-player-slide').change((e) => {
    const $this = $(e.currentTarget);
    $('#num-human-player-text').html($this.val());
});
