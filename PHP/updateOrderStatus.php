<?php

require_once('PrestaShop-webservice-lib-master/PSWebServiceLibrary.php');

if (isset($argv)) {
    try {
        // $argv[1] = store
        // $argv[2] = order id
        // $argv[3] = api key

        $webService = new PrestaShopWebservice('https://' . $argv[1] . '.ma/', $argv[3], false);
    
        $xml = $webService->get([
            'resource' => 'orders',
            'id' => $argv[2], 
        ]);

        $orderFields = $xml->order->children();

        // 4 = id of status "Expedié" or "Encours de livraison"
        // See https://DOMAIN/ADMINURL/index.php?controller=AdminStatuses&token=TOKEN
        $orderFields->current_state = 4;

        $updatedXml = $webService->edit([
            'resource' => 'orders',
            'id' => (int) $orderFields->id,
            'putXml' => $xml->asXML(),
        ]);

        $orderFields = $updatedXml->orders->children();

        echo $argv[1] . '-' .$argv[2] . ' : Encours de livraison' . PHP_EOL;
    }
    catch (PrestaShopWebserviceException $ex) {
        echo $argv[1] . '-' .$argv[2] . ': ERROR!\n';
        } 
    }

else {
        echo "missing Store/ID/APIKey";
    }
