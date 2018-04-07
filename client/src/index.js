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

    retrieveParam(cycle, 5, 'urgent', $(dom.children()[1]));
    retrieveParam(cycle, 5, 'non-urgent', $(dom.children()[2]));
    retrieveParam(cycle, 5, 'inventory', $(dom.children()[3]));
}

function uploadHCDecisions() {
    const satUrgent = $('#hc-satisfy-urgent-input').val();
    const satNonUrgent = $('#hc-satisfy-non-urgent-input').val();
    const orderDS1 = $('#hc-order-from-ds1-input').val();
    const orderDS2 = $('#hc-order-from-ds2-input').val();

    const req1 = $.ajax({
        url: '/api/make_decision', 
        method: 'GET',
        dataType: 'json',
        data: {
            token,
            'decisionName': 'satisfy_urgent',
            'decisionValue': satUrgent
        }
    });

    const req2 = $.ajax({
        url: '/api/make_decision', 
        method: 'GET',
        dataType: 'json',
        data: {
            token,
            'decisionName': 'satisfy_non_urgent',
            'decisionValue': satNonUrgent
        }
    });

    const req3 = $.ajax({
        url: '/api/make_decision', 
        method: 'GET',
        dataType: 'json',
        data: {
            token,
            'decisionName': 'order_from_ds1',
            'decisionValue': orderDS1
        }
    });

    const req4 = $.ajax({
        url: '/api/make_decision', 
        method: 'GET',
        dataType: 'json',
        data: {
            token,
            'decisionName': 'order_from_ds2',
            'decisionValue': orderDS2
        }
    });

    return req1, req2, req3, req4;
}

function hcNextPeriod() {
    $.when(uploadHCDecisions()).then( () => {
        $.ajax({
            url: '/api/next_period', 
            method: 'GET',
            dataType: 'json',
            data: {
                token,
            },
            success: () => {
                cycle++;
                retrieveHealthCenterInformation();
            }
        });
    });
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
$('#hc-next-period-button').click(() => hcNextPeriod());
