let token = '';
let cycle = 0;

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
    const role = $('input[name=role]:checked').val(); 

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

            if (role === 'health-center') {
                startPlayingHealthCenter();
            } else if (role === 'manufacturer') {
                startPlayingManufacturer();
            }

        }
    });
}

function joinGame() {
    //console.error('Not implemented');
}

function startPlayingHealthCenter() {
    $('#health-center-play').show();
    retrieveHealthCenterInformation();
}

function startPlayingManufacturer() {
    $('#manufacturer-play').show();
    retrieveManufacturerInformation();
}

function retrieveParam(paramName, dom = null, onSuccess = null) {
    $.ajax({
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
        </tr>`);
    $('#health-center-data-table').append(dom);

    retrieveParam('urgent', $(dom.children()[1]));
    retrieveParam('non-urgent', $(dom.children()[2]));
    retrieveParam('inventory', $(dom.children()[3]));
    retrieveParam('lost-urgent', $(dom.children()[4]));
    retrieveParam('lost-non-urgent', $(dom.children()[5]));
    retrieveParam('on-order', $(dom.children()[6]));
    retrieveParam('received-delivery', $(dom.children()[7]));
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


function uploadHCDecisions() {
    const satUrgent = $('#hc-satisfy-urgent-input').val();
    const satNonUrgent = $('#hc-satisfy-non-urgent-input').val();
    const orderDS1 = $('#hc-order-from-ds1-input').val();
    const orderDS2 = $('#hc-order-from-ds2-input').val();

    const req1 = $.ajax({
        url: '/api/make_decision', 
        method: 'GET',
        data: {
            token,
            'decisionName': 'satisfy_urgent',
            'decisionValue': satUrgent
        }
    });

    const req2 = $.ajax({
        url: '/api/make_decision', 
        method: 'GET',
        data: {
            token,
            'decisionName': 'satisfy_non_urgent',
            'decisionValue': satNonUrgent
        }
    });

    const req3 = $.ajax({
        url: '/api/make_decision', 
        method: 'GET',
        data: {
            token,
            'decisionName': 'order_from_ds1',
            'decisionValue': orderDS1
        }
    });

    const req4 = $.ajax({
        url: '/api/make_decision', 
        method: 'GET',
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

function uploadMNDecisions() {
    const produce = $('#mn-produce').val();
    const satisfyDS1 = $('#mn-satisfy-ds1').val();
    const satisfyDS2 = $('#mn-satisfy-ds2').val();

    const req1 = $.ajax({
        url: '/api/make_decision', 
        method: 'GET',
        data: {
            token,
            'decisionName': 'produce',
            'decisionValue': produce,
        }
    });

    const req2 = $.ajax({
        url: '/api/make_decision', 
        method: 'GET',
        data: {
            token,
            'decisionName': 'satisfy_ds1',
            'decisionValue': satisfyDS1
        }
    });


    const req3 = $.ajax({
        url: '/api/make_decision', 
        method: 'GET',
        data: {
            token,
            'decisionName': 'satisfy_ds2',
            'decisionValue': satisfyDS2
        }
    });

    return req1, req2, req3;
}


function mnNextPeriod() {
    $.when(uploadMNDecisions()).then( () => {
        $.ajax({
            url: '/api/next_period', 
            method: 'GET',
            data: {
                token,
            },
            success: () => {
                cycle++;
                retrieveManufacturerInformation();
            }
        });
    });

}

$('#create-game-dialog').hide();
$('#join-game-dialog').hide();
$('#health-center-play').hide();
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
