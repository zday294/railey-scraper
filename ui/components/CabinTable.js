app.component('cabin-table', {
    props: {
        cabins: {
            type: Array,
            required: true
        },
        weekends: {
            type: Array,
            required: true
        }
    },
    template: 
    /*html*/
    `
    <div class="table"> 
        <table>
            <thead>
                <tr>
                    <th>Cabin</th>
                    <th class='amenity-header'>Home Theater</th>
                    <th class='amenity-header'>Pool</th>
                    <th class='amenity-header'>Pool Table</th>
                    <th class='bed-header'>Upper Beds</th>
                    <th class='bed-header'>Main Beds</th>
                    <th class='bed-header'>Lower Beds</th>
                    <th class='bed-header'>Garage Beds</th>
                    <th class='bed-header'>Total Beds</th>
                    <th class='bed-header'>Occupancy</th>
                    <th>July Weekend 3</th>
                    <th>July Weekend 4</th>
                    <th>Average Price</th>
                    <th>Score</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="cabin in cabins"> <cabin-line :cabin="cabin" :weekends="weekends"></cabin-line> </tr>

                <tr class='average-row'>
                    <td class='cabin-name'>Weekend Average</td>
                    <td>—</td>
                    <td>—</td>
                    <td>—</td>
                    <td>—</td>
                    <td>—</td>
                    <td>—</td>
                    <td>—</td>
                    <td>—</td>
                    <td>—</td>
                    <!-- for weekend in weekends here -->
                    <td v-for="weekend in weekends" :style="heatStyle(averageCabinPriceForWeekend(weekend))">{{'$'}}{{formatRate(averageCabinPriceForWeekend(weekend))}}</td>
                    <td>—</td>
                    <td>—</td>
                </tr>
            </tbody>
        </table>
    </div>
    `,
    methods: {
        averageCabinPriceForWeekend(weekend) {
            availableCabins = 0
            sum = 0
            this.cabins.forEach(cabin => {
                weekendPrice = cabin.prices[weekend]
                if (weekendPrice != undefined && weekendPrice != NaN){
                    availableCabins++
                    sum += weekendPrice
                }
            });

            return sum / availableCabins
        },
        heatStyle(price) {
            (price / 5000).toFixed(2)
            return 'background-color: rgba(255, 152, 0, ' + (price / 5000).toFixed(2) + '); color: white; font-weight: bold;'
        }
        ,
        formatRate(value) {
            return parseFloat(value).toFixed(2);
        }
    }

})