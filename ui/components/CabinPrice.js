app.component('cabin-price', {
    props: {
        price: {
            required: false
        }
    },
    template:
    /*html*/
    `
    <td v-if="price == undefined" class='unavailable'>-</td>
    <td v-else class='available'> {{'$'}}{{formatRate(price)}}</td>
    `,
    methods: {
        formatRate(value) {
            return parseFloat(value).toFixed(2);
        }
    }
})