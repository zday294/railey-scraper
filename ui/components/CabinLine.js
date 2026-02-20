app.component('cabin-line', {
    props: {
        cabin: {
            required: true
        },
        weekends: {
            type: Array,
            require: true
        }
    },
    template: 
    /*html*/
    `
        <td class='cabin-name'><a href='https://www.deepcreek.com/vacation-rentals/alpine-lodge' target='_blank'>{{ cabin.name }}</a></td>
        
        <td v-if="hasTheater" class='has-amenity'>✓</td>
        <td v-else class='no-amenity'>—</td>
        
        <td v-if="hasPool" class='has-amenity'>✓</td>
        <td v-else class='no-amenity'>—</td>

        <td v-if="hasPoolTable" class='has-amenity'>✓</td>
        <td v-else class='no-amenity'>—</td>

        
        <td class='bed-info'>{{ cabin.upperBeds }}</td>
        <td class='bed-info'>{{ cabin.mainBeds }}</td>
        <td class='bed-info'>{{ cabin.lowerBeds }}</td>
        <td class='bed-info'>{{ cabin.garageBeds }}</td>
        <td class='bed-info'><strong> {{ totalBeds }}</strong></td>
        <td class='bed-info'><strong>{{ cabin.occupancy }}</strong></td>
        
        <cabin-price v-for="weekend in this.weekends" :price="this.cabin.prices[weekend]" :bestPrice="this.lowestWeekend" ></cabin-price>
        
        <td><strong>{{'$'}}{{formatRate(averagePrice)}}</strong></td>
        <td><strong>{{cabin.score}}</strong></td>
    `,
    methods: {
        formatRate(value) {
            return parseFloat(value).toFixed(2);
        }
    },
    computed: {
        hasTheater() {
            return this.cabin.amenities.indexOf('Home Theater') > -1
        },
        hasPool() {
            return this.cabin.amenities.indexOf('Pool') > -1
        },
        hasPoolTable() {
            return this.cabin.amenities.indexOf('Pool Table') > -1
        },
        totalBeds() {
            return this.cabin.upperBeds + this.cabin.lowerBeds + this.cabin.mainBeds + this.cabin.garageBeds
        },
        averagePrice() {
            sum = 0
            this.weekends.forEach(weekend => {
                price = this.cabin.prices[weekend]
                if (price != undefined)
                    sum += price
            });

            return (sum / Object.keys(this.cabin.prices).length)
        },
        lowestWeekend()  {
            pricesOnly = Object.values(this.cabin.prices)
            
            const min = pricesOnly.reduce((prev, current) => (prev && prev < current) ? prev : current)
            return min
        }
    }
})