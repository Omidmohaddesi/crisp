let token = '';
let cycle = 0;
let role = '';

function showCreateGameDialog() {
    $('#create-game-dialog').show();
    $('#menu').hide();
}


function showJoinGameDialog() {
    $('#join-game-dialog').show();
    $('#menu').hide();
}

function createGame() {
    const numHumanPlayer = $('#num-human-player-slide').val();
    role = $('input[name=role]:checked').val(); 

    const req = {
        numHumanPlayer,
        role,
    };

    $.ajax({
        url: '/api/create_game', 
        method: 'GET',
        data: req,
        datatype: 'text',
        success: (data) => {
            token = data;
            //const gameHashId = data.hash_id;
            
            $('#create-game-dialog').hide();

            if (numHumanPlayer > 1) {
                showWaitForOtherPlayerDialog();
            } else {
                if (role === 'health-center') {
                    startPlayingHealthCenter();
                } else if (role == 'distributor') {
                    startPlayingDistributor();
                }else if (role === 'manufacturer') {
                    startPlayingManufacturer();
                }
            }

            getGameHashID();

        }
    });
}

function checkIfAllOtherPlayersJoined() {
    $.ajax({
        url: '/api/is_all_human_player_joined',
        method: 'GET',
        data: {
            token: token,
        },
        datatype: 'text',
        success: (data) => {
            if (data === 'true') {
                $('#wait-for-other-players').hide();
                if (role === 'health-center') {
                    startPlayingHealthCenter();
                } else if (role == 'distributor') {
                    startPlayingDistributor();
                }else if (role === 'manufacturer') {
                    startPlayingManufacturer();
                }
            } else {
                setTimeout(checkIfAllOtherPlayersJoined, 1000);
            }
        }
    });
}

function showWaitForOtherPlayerDialog() {
    $('#wait-for-other-players').show();
    checkIfAllOtherPlayersJoined();
}

function getGameHashID() {
    $.ajax({
        url: '/api/get_game_hash_id',
        method: 'GET',
        data: {
            token
        },
        datatype: 'text',
        success: (data) => {
            $('#game_hash_id').html(data);
        }
    });
}

function joinGame() {
    let hashId = $('#join-game-hash-id').val();
    role = $('input[name=join-role]:checked').val(); 

    $.ajax({
        url: '/api/join_game', 
        method: 'GET',
        data: {
            hashId,
            role,
        },
        datatype: 'text',
        success: (data) => {
            token = data;
            $('#join-game-dialog').hide();
            showWaitForOtherPlayerDialog();
            $('#game_hash_id').html(hashId);
        }
    });

}

function startPlayingHealthCenter() {
    $('#health-center-play').show();
    retrieveHealthCenterInformation();
}

function startPlayingDistributor() {
    $('#distributor-play').show();
    retrieveDistributorInformation();
}

function startPlayingManufacturer() {
    $('#manufacturer-play').show();
    retrieveManufacturerInformation();
}

function retrieveParam(paramName, dom = null, onSuccess = null) {
    return $.ajax({
        url: '/api/get_game_param', 
        method: 'GET',
        datatype: 'text',
        data: {
            token,
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

function uploadDecision(name, value) {
    return $.ajax({
        url: '/api/make_decision', 
        method: 'GET',
        data: {
            token,
            'decisionName': name,
            'decisionValue': value,
        }
    });
}

function checkIfServerMovedToNextCycle(onDone) {
    $.ajax({
        url: '/api/get_game_param', 
        method: 'GET',
        data: {
            token,
            paramName: 'cycle',
        },
        datatype: 'text',
        success: (data) => {
            const serverCycle = parseInt(data);
            if (serverCycle === cycle) {
                setTimeout(checkIfServerMovedToNextCycle, 1000); 
            } else if (serverCycle == cycle + 1) {
                cycle = serverCycle;
                $('input').prop('disabled', false);
                if (onDone) {
                    onDone();
                }
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
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
        </tr>`);
    $('#health-center-data-table').append(dom);

    retrieveParam('urgent', $(dom.children()[1]));
    retrieveParam('non-urgent', $(dom.children()[2]));
    retrieveParam('inventory', $(dom.children()[3]));
    retrieveParam('lost-urgent', $(dom.children()[4]));
    retrieveParam('lost-non-urgent', $(dom.children()[5]));
    retrieveParam('on-order', $(dom.children()[6]));
    retrieveParam('received-delivery', $(dom.children()[7]));
    retrieveParam('order-to-ds1', $(dom.children()[8]));
    retrieveParam('order-to-ds2', $(dom.children()[9]));
}


function uploadHCDecisions() {
    const satUrgent = $('#hc-satisfy-urgent-input').val();
    const req1 = uploadDecision('satisfy_urgent', satUrgent);

    const satNonUrgent = $('#hc-satisfy-non-urgent-input').val();
    const req2 = uploadDecision('sat_non_urgent', satNonUrgent);

    const orderDS1 = $('#hc-order-from-ds1-input').val();
    const req3 = uploadDecision('order_from_ds1', orderDS1);

    const orderDS2 = $('#hc-order-from-ds2-input').val();
    const req4 = uploadDecision('order_from_ds2', orderDS2);

    return req1, req2, req3, req4;
}

function hcNextPeriod() {
    $('input').prop('disabled', true);
    $.when(uploadHCDecisions()).then( () => {
        $.ajax({
            url: '/api/next_period', 
            method: 'GET',
            data: {
                token,
            },
            success: () => {
                checkIfServerMovedToNextCycle(
                    retrieveHealthCenterInformation());
            }
        });
    });
}

function retrieveManufacturerInformation() {
    const dom = $(
        `<tr>
            <td>${cycle}</td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
        </tr>`);
    $('#manufacturer-data-table').append(dom);

    retrieveParam('in-production', $(dom.children()[1]));
    retrieveParam('inventory', $(dom.children()[2]));
    retrieveParam('on-order', $(dom.children()[3]));
    retrieveParam('backlog-ds1', $(dom.children()[4]));
    retrieveParam('backlog-ds2', $(dom.children()[5]));
}



function uploadMNDecisions() {
    const produce = $('#mn-produce').val();
    const req1 = uploadDecision('produce', produce);

    const satisfyDS1 = $('#mn-satisfy-ds1').val();
    const req2 = uploadDecision('satidfy_ds1', satisfyDS1);

    const satisfyDS2 = $('#mn-satisfy-ds2').val();
    const req3 = uploadDecision('satidfy_ds2', satisfyDS2);

    return req1, req2, req3;
}


function mnNextPeriod() {
    $('input').prop('disabled', true);
    $.when(uploadMNDecisions()).then( () => {
        $.ajax({
            url: '/api/next_period', 
            method: 'GET',
            data: {
                token,
            },
            success: () => {
                checkIfServerMovedToNextCycle(
                    retrieveManufacturerInformation);
            }
        });
    });

}

function retrieveDistributorInformation() {
    const dom = $(
        `<tr>
            <td>${cycle}</td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
        </tr>`);
    $('#distributor-data-table').append(dom);

    retrieveParam('inventory', $(dom.children()[1]));
    retrieveParam('on-order', $(dom.children()[2]));
    retrieveParam('backlog-hc1', $(dom.children()[3]));
    retrieveParam('backlog-hc2', $(dom.children()[4]));
}



function uploadDSDecisions() {
    const satisfyHC1 = $('#ds-satisfy-hc1').val();
    const req1 =uploadDecision('satisfy_hc1', satisfyHC1);
    const satisfyHC2 = $('#ds-satisfy-hc2').val();
    const req2 =uploadDecision('satisfy_hc2', satisfyHC2);
    const orderMN1 = $('#ds-order-mn1').val();
    const req3 =uploadDecision('order_from_mn1', orderMN1);
    const orderMN2 = $('#ds-order-mn2').val();
    const req4 =uploadDecision('order_from_mn2', orderMN2);

    return req1, req2, req3, req4;
}


function dsNextPeriod() {
    $('input').prop('disabled', true);
    $.when(uploadDSDecisions()).then( () => {
        $.ajax({
            url: '/api/next_period', 
            method: 'GET',
            data: {
                token,
            },
            success: () => {
                checkIfServerMovedToNextCycle(
                    retrieveDistributorInformation);
            }
        });
    });

}

$('#create-game-dialog').hide();
$('#join-game-dialog').hide();
$('#wait-for-other-players').hide();
$('#health-center-play').hide();
$('#distributor-play').hide();
$('#manufacturer-play').hide();
$('#create-game-button').click(() => showCreateGameDialog());
$('#join-game-button').click(() => showJoinGameDialog());
$('#create-game-ok-button').click(() => createGame());
$('#join-game-ok-button').click(() => joinGame());
$('#num-human-player-slide').change((e) => {
    const $this = $(e.currentTarget);
    $('#num-human-player-text').html($this.val());
});
$('#hc-next-period-button').click(() => hcNextPeriod());
$('#mn-next-period-button').click(() => mnNextPeriod());
$('#ds-next-period-button').click(() => dsNextPeriod());
