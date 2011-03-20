template = '''
    <div class="tweet" id="t-{{id}}">
        <img class="tweet-img" src="{{profile_image_url}}">
        <div class="tweet-content">
            <div class="tweet-user">@{{from_user}}</div><div class="tweet-text">{{text}}</div>
            <div class="tweet-date">{{printed}}</div>
        </div>
    </div>
'''

timeAgo = (date1, date2, granularity) ->
    self = this

    periods =
        week : 604800
        day : 86400
        hour : 3600
        minute : 60
        second : 1

    if not granularity
        granularity = 5

    date1 = date1.getTime() / 1000
    date2 = date2.getTime() / 1000

    if date1 > date2
        difference = date1 - date2
    else
        difference = date2 - date1

    output = ''

    for period, value of periods
        value = periods[period]

        if difference >= value
            time = Math.floor(difference / value)
            difference %= value

            output = output +  time + ' '

            if time > 1
                output = output + period + 's '
            else
                output = output + period + ' '

        granularity--

        if granularity == 0
            break

    output + ' ago'


class Searcher

    constructor: (@hashtag, @template, @baseelem,@max_tweets) ->
        @last_tweet = null
        @tweets = []
        if not @max_tweets
            @max_tweets=5

    search: () ->
        if @last_tweet
            url = "http://search.twitter.com/search.json?q=#{@hashtag}&since_id=#{@last_tweet}"
        else
            url = "http://search.twitter.com/search.json?q=#{@hashtag}&rpp="+@max_tweets
        console.log(url)
        $.ajax({
            url: url
            dataType: 'jsonp'
            success: (data) =>
                if not @last_tweet
                    data.results.sort( (a, b) ->
                        return new Date(a.created_at) - new Date(b.created_at)
                    )

                if data.results.length>0
                    for item in data.results
                        d = new Date(Date.parse(item.created_at))
                        print_date = timeAgo(d, new Date())
                        item.printed = print_date
                        @tweets.unshift(item)
                        h = $(Mustache.to_html(@template, item))
                        e = $("<div />").html(h)
                        console.log(e.height())
                        e.hide()
                        $(@baseelem).prepend(e)

                        @last_tweet = item.id_str # remember it

                        # show it
                        e.slideDown(300)

                        if @tweets.length>@max_tweets
                            last = @tweets.pop()
                            $("#t-"+last.id).slideUp(300, () ->
                                $("#t-"+last.id).remove()
                            )

                    #twttr.anywhere( (T)  ->
                        #    T.hovercards()
                    #)
        })

    loop: () =>
        setTimeout(@work, 4000)

    work: () =>
        @search()
        @loop()


$(document).ready( () ->
    searcher = new Searcher("lybia",template, "#tweets")
    searcher.work()
)
