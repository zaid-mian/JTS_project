import json

def convert():
    try:
        with open('crm_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: crm_data.json not found!")
        return

    converted = []
    for item in data:
        model = item['model']
        pk = item['pk']
        fields = item['fields']

        if model == 'crm.product':
            new_model = 'catalog.product'
            fields['is_active'] = True
            fields['display_order'] = 0

        elif model == 'crm.feature':
            new_model = 'catalog.module'
            fields['is_active'] = True
            fields['display_order'] = 0

        elif model == 'crm.pricingplan':
            new_model = 'catalog.pricingplan'
            fields['is_active'] = True
            fields['display_order'] = 0

        elif model == 'crm.planfeature':
            new_model = 'catalog.planmodule'
            fields['module'] = fields.pop('feature')

        else:
            new_model = model

        # Ensure updated_at is populated if created_at exists but updated_at is missing (avoids IntegrityError)
        if 'created_at' in fields and 'updated_at' not in fields:
            fields['updated_at'] = fields['created_at']

        converted.append({
            'model': new_model,
            'pk': pk,
            'fields': fields
        })


    with open('catalog_data.json', 'w', encoding='utf-8') as f:
        json.dump(converted, f, indent=4, ensure_ascii=False)
    print("Successfully converted fixture to catalog_data.json. Total objects:", len(converted))

if __name__ == '__main__':
    convert()
