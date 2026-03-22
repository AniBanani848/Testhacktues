from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import ChatMessage, Friendship


@login_required
def friend_list(request):
    uid = request.user.id
    friendships = Friendship.objects.filter(
        Q(from_user_id=uid) | Q(to_user_id=uid),
    ).select_related('from_user', 'to_user')

    pending_in = friendships.filter(to_user=request.user, status=Friendship.Status.PENDING)
    pending_out = friendships.filter(from_user=request.user, status=Friendship.Status.PENDING)
    accepted = friendships.filter(status=Friendship.Status.ACCEPTED)

    return render(
        request,
        'chat/friends.html',
        {
            'accepted': accepted,
            'pending_in': pending_in,
            'pending_out': pending_out,
        },
    )


@login_required
def add_friend(request):
    if request.method != 'POST':
        return redirect('friend_list')
    username = (request.POST.get('username') or '').strip()
    if not username:
        messages.error(request, 'Enter a username.')
        return redirect('friend_list')

    other = User.objects.filter(username__iexact=username).first()
    if not other:
        messages.error(request, 'No user with that username.')
        return redirect('friend_list')
    if other.id == request.user.id:
        messages.error(request, 'You cannot add yourself.')
        return redirect('friend_list')

    reverse_pending = Friendship.objects.filter(
        from_user=other,
        to_user=request.user,
        status=Friendship.Status.PENDING,
    ).first()
    if reverse_pending:
        reverse_pending.status = Friendship.Status.ACCEPTED
        reverse_pending.save(update_fields=['status'])
        messages.success(request, f'You are now friends with {other.username}. Open chat to say hi.')
        return redirect('chat_room', friendship_id=reverse_pending.pk)

    existing = Friendship.objects.filter(from_user=request.user, to_user=other).first()
    if existing:
        if existing.status == Friendship.Status.ACCEPTED:
            messages.info(request, 'You are already friends.')
            return redirect('chat_room', friendship_id=existing.pk)
        messages.info(request, 'Friend request already sent.')
        return redirect('friend_list')

    Friendship.objects.create(
        from_user=request.user,
        to_user=other,
        status=Friendship.Status.PENDING,
    )
    messages.success(request, f'Friend request sent to {other.username}.')
    return redirect('friend_list')


@login_required
def accept_friend(request, pk):
    fs = get_object_or_404(Friendship, pk=pk, to_user=request.user, status=Friendship.Status.PENDING)
    fs.status = Friendship.Status.ACCEPTED
    fs.save(update_fields=['status'])
    messages.success(request, 'Friend request accepted.')
    return redirect('chat_room', friendship_id=fs.pk)


@login_required
def decline_friend(request, pk):
    fs = get_object_or_404(Friendship, pk=pk, to_user=request.user, status=Friendship.Status.PENDING)
    fs.delete()
    messages.info(request, 'Request declined.')
    return redirect('friend_list')


@login_required
def chat_room(request, friendship_id):
    fs = get_object_or_404(
        Friendship.objects.select_related('from_user', 'to_user'),
        pk=friendship_id,
        status=Friendship.Status.ACCEPTED,
    )
    if request.user not in (fs.from_user, fs.to_user):
        raise PermissionDenied()

    msgs = list(
        ChatMessage.objects.filter(friendship=fs)
        .select_related('sender')
        .order_by('-created_at')[:200]
    )
    msgs.reverse()
    other = fs.other_user(request.user)

    return render(
        request,
        'chat/room.html',
        {
            'friendship': fs,
            'other_user': other,
            'chat_messages': msgs,
        },
    )
