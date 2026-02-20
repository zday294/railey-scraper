app.component('cabin-table', {
    props: {
        cabins: {
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
            <tr v-for="cabin in cabins"> <cabin-line :cabin="cabin"></cabin-line> </tr>
            </tbody>
        </table>
    </div>
    `

})